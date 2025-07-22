"use client"

import { CopilotKit } from "@copilotkit/react-core"
import type React from "react"

/**
 * Provides CopilotKit context to the component tree so that
 * `useCopilotAction` calls work without throwing errors.
 */
export function CopilotProvider({ children }: { children: React.ReactNode }) {
  return <CopilotKit runtimeUrl="/api/copilotkit">{children}</CopilotKit>
}
