import type React from "react"
import type { Metadata } from "next"
import { Inter } from "next/font/google"
import "./globals.css"
import { ThemeProvider } from "@/components/theme-provider"
import { CopilotKit } from "@copilotkit/react-core"
import { 
  CopilotPopup, 
  CopilotChatSuggestion, 
  RenderSuggestion,
  RenderSuggestionsListProps,
  MessagesProps,
  useChatContext,
  HeaderProps,
  ButtonProps,
  WindowProps

 } from "@copilotkit/react-ui"
import "@copilotkit/react-ui/styles.css"

const inter = Inter({ subsets: ["latin"] })

export const metadata: Metadata = {
  title: "Accessible Solutions - Help Happens Here",
  description:
    "Making help accessible and simple through innovative, trauma-informed, client-centered solutions in Oregon.",
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={inter.className}>
       <CopilotKit  publicApiKey="ck_pub_8274d21b3e208c50f988f5fdf2b702de" runtimeUrl="/api/copilotkit" agent="supervisor">
          <ThemeProvider attribute="class" defaultTheme="dark" enableSystem disableTransitionOnChange>
            {children}
          
            <CopilotPopup
              instructions="You are Sybl, a trauma-informed AI assistant for Accessible Solutions. Your goal is to help users, you may respond directly if it is a simple question that you have knowledge about, otherwise call a tool. You can pass tasks to your agent tools- phone, tts, research (general, person, company, job) or you can find local resources, create resumes/ cover letters. Always be compassionate and supportive."
              labels={{
                title: "Sybl - Help Happens Here",
                initial: "Hi! I'm Sybl. How can I support you today?",
              }}
              defaultOpen={false}
              clickOutsideToClose={true}
            />
          </ThemeProvider>
        </CopilotKit>
      </body>
    </html>
  )
}
