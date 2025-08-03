import {
  CopilotRuntime,
  ExperimentalEmptyAdapter,
  copilotRuntimeNextJSAppRouterEndpoint,
  LangGraphHttpAgent,
} from "@copilotkit/runtime";
import { NextRequest } from "next/server";
 
// You can use any service adapter here for multi-agent support.
const serviceAdapter = new ExperimentalEmptyAdapter();
 
const runtime = new CopilotRuntime({
  agents: {
      'supervisor': new LangGraphHttpAgent({ url: "http://localhost:8000/copilotkit" })},
  
});
 
export const POST = async (req: NextRequest) => {
  const { handleRequest } = copilotRuntimeNextJSAppRouterEndpoint({
    runtime,
    serviceAdapter,
    endpoint: "/api/copilotkit",
  });
 
  return handleRequest(req);
};