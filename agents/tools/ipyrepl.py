
"""Public API
==========
run_python(code: str, *, session: str | None = None, timeout: int = 30) -> dict
    • If *session* is None ⇒ stateless (identical to the non‑persistent version).
    • Otherwise, the kernel for that session is reused until `reset_session(sess)`
      or the process exits.
reset_session(session: str) -> None
    Kills the kernel + client and frees resources.

Notes
-----
• Uses jupyter_client (kernel_manager) so we stay pure‑Python – no "jupyter" CLI
  required at runtime.
• Each session communicates over in‑proc zmq channels; still protected by the
  outer `multiprocessing` timeout + kill guard.
• We still capture Matplotlib figures & PIL images by inspecting the kernel
  user_ns via `%who` + `get_ipython().user_ns` executed inside the kernel.
"""

from __future__ import annotations

import multiprocessing as mp, os, time, json, base64, traceback
from io import BytesIO, StringIO
from typing import Optional, Dict
from contextlib import redirect_stdout, redirect_stderr

import matplotlib.pyplot as plt  # figures rendered inside worker
from PIL import Image

from jupyter_client import KernelManager
from jupyter_client.manager import start_new_kernel
from jupyter_client.client import BlockingKernelClient

mp.set_start_method("spawn", force=True)

# ───────────────────────────────────────────────────────────────────────────────
# Globals (lives only inside the worker process)
_sessions: Dict[str, BlockingKernelClient] = {}

# Helper: base64 encode images --------------------------------------------------

def _b64_png(buf: bytes) -> str:
    return base64.b64encode(buf).decode()


def _extract_images(ns):
    imgs = []
    for num in plt.get_fignums():
        fig = plt.figure(num)
        buf = BytesIO()
        fig.savefig(buf, format="png", bbox_inches="tight")
        imgs.append(_b64_png(buf.getvalue()))
        plt.close(fig)
    for obj in ns.values():
        if isinstance(obj, Image.Image):
            buf = BytesIO()
            obj.save(buf, format="PNG")
            imgs.append(_b64_png(buf.getvalue()))
    return imgs

# Worker -----------------------------------------------------------------------

def _worker(code: str, session: Optional[str], timeout: int, q: mp.Queue):
    out, err = StringIO(), StringIO()
    try:
        with redirect_stdout(out), redirect_stderr(err):
            if session:
                km, kc = _sessions.get(session, (None, None))
                if kc is None or not km.is_alive():
                    km, kc = start_new_kernel(kernel_name="python3")
                    _sessions[session] = (km, kc)
            else:
                km, kc = start_new_kernel(kernel_name="python3")

            kc.execute(code)
            kc.wait_for_ready(timeout=timeout)
            reply = kc.get_shell_msg(timeout=timeout)["content"]
            status = reply.get("status")
            if status == "error":
                raise RuntimeError("\n".join(reply.get("traceback", [])))
            # fetch last result via _ in user_ns
            kc.execute("import json, inspect, matplotlib.pyplot as plt, sys")
            kc.execute("_last = locals().get('_', None)")
            kc.execute("import dill, base64, types, builtins")
            kc.execute("print(repr(_last))")
            # user namespace images
            kc.execute("import inspect, matplotlib.pyplot as plt")
            ns_imgs_code = (
                "import json, base64, io, matplotlib.pyplot as plt, sys;"
                "from PIL import Image;"
                "def _cap():\n"
                " imgs=[]\n"
                " import builtins, gc;ns=globals();\n"
                " for num in plt.get_fignums():\n"
                "  fig=plt.figure(num);b=io.BytesIO();fig.savefig(b,format='png');b.seek(0);\n"
                "  imgs.append(base64.b64encode(b.read()).decode());plt.close(fig)\n"
                " for v in ns.values():\n"
                "  from PIL import Image as _Image;\n"
                "  if isinstance(v,_Image):b=io.BytesIO();v.save(b,format='PNG');b.seek(0);imgs.append(base64.b64encode(b.read()).decode())\n"
                " print(json.dumps(imgs))\n"
            )
            kc.execute(ns_imgs_code)
            images = json.loads(kc.get_stdout()[-1]) if session else []

        data = dict(stdout=out.getvalue(), stderr=err.getvalue(), images=images)
    except Exception as e:
        data = dict(error="".join(traceback.format_exception(None, e, e.__traceback__)),
                    stdout=out.getvalue(), stderr=err.getvalue(), images=[])
    q.put(data)

# Public API --------------------------------------------------------------------

def run_python(code: str, *, session: str | None = None, timeout: int = 30) -> dict:
    """Execute code, optionally in a persistent *session*.

    Returns `{stdout, stderr, images, error?}` dict.
    """
    q: mp.Queue = mp.SimpleQueue()
    p = mp.Process(target=_worker, args=(code, session, timeout, q))
    p.start()
    p.join(timeout)
    if p.is_alive():
        p.kill(); p.join()
        return {"error": "Execution timed out", "images": []}
    return q.get() if not q.empty() else {"stdout": ""}


def reset_session(session: str):
    km, kc = _sessions.pop(session, (None, None))
    if kc:
        kc.shutdown()
        km.shutdown_kernel(now=True)

