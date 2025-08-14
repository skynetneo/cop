declare var ParticleSlider: any;
declare var dat: any;

const BASE64_DATA_URL = "data:image/png;base64,"; // <-- paste full data URL

function loadScript(src: string): Promise<void> {
  return new Promise((resolve, reject) => {
    const s = document.createElement("script");
    s.src = src;
    s.async = true;
    s.onload = () => resolve();
    s.onerror = () => reject(new Error(`Failed to load ${src}`));
    document.head.appendChild(s);
  });
}

function buildMarkup() {
  // Recreate CodePen's HTML in JS so the page can be empty initially
  document.body.id = "particle-slider";

  const slides = document.createElement("div");
  slides.className = "slides";

  const slide = document.createElement("div");
  slide.id = "first-slide";
  slide.className = "slide";
  slide.dataset.src = BASE64_DATA_URL; // what ParticleSlider reads

  slides.appendChild(slide);
  document.body.appendChild(slides);
}

// Monkey-patch to get “rising + reborn” behavior
function patchRebirth(ps: any) {
  // Re-seed particles below the canvas on init
  const origInit = ParticleSlider.prototype.init;
  ParticleSlider.prototype.init = function (force?: boolean) {
    origInit.call(this, force);
    this.mouseForce = 6000; // tame hover push

    let p = this.pxlBuffer.first;
    while (p) {
      if (!p._reborn) {
        p.x = p.gravityX + (Math.random() * 40 - 20);      // near target x
        p.y = this.ch + 120 + Math.random() * 200;         // well below canvas
        p.velocityY = -(0.8 + Math.random() * 1.6);        // initial upward kick
        p.velocityX = (Math.random() * 0.6 - 0.3);
        p._reborn = true;
      }
      p = p.next;
    }
  };

  // Gentle updraft every frame
  const P = ParticleSlider.prototype.Particle;
  const origMove = P.prototype.move;
  P.prototype.move = function () {
    this.velocityY += -0.03; // negative is “up” in canvas coords
    return origMove.call(this);
  };

  // Let the system settle (don’t constantly reshuffle)
  ps.restless = false;
  ps.init(true);
}

async function main() {
  buildMarkup();


  // Desktop vs mobile sizing (matches your CodePen intent)
  const isMobile = /mobile/i.test(navigator.userAgent);
  const isSmall = window.innerWidth < 1000;

  const ps = new ParticleSlider({
    ptlGap: isMobile || isSmall ? 3 : 0,
    ptlSize: isMobile || isSmall ? 3 : 1,
    width: 1e9,
    height: 1e9
  });

  patchRebirth(ps);

  // Quick GUI to tweak live (optional)
  const gui = new dat.GUI();
  gui.add(ps, "ptlGap", 0, 5, 1).onChange(() => ps.init(true));
  gui.add(ps, "ptlSize", 1, 5, 1).onChange(() => ps.init(true));
  gui.add(ps, "restless");
  gui.addColor(ps, "color").onChange((value: string) => {
    ps.monochrome = true;
    ps.setColor(value);
    ps.init(true);
  });

  // Re-trigger assembly on click (like your snippet)
  window.addEventListener("click", () => ps.init(true), false);
}

main().catch(console.error);