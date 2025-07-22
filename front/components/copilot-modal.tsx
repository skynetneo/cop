//this has been replaced by CopilotKit popup

"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { X, MessageCircle, Brain, Search, AlertTriangle, FileText, User } from "lucide-react"
import { motion, AnimatePresence } from "framer-motion"
import { cn } from "@/lib/utils"
import { ResourceCarousel, type Resource } from "@/components/ui/resource-card"
import { searchResources } from "@/lib/resource-search"
import { ResumeBuilderForm, type ResumeData } from "@/components/resume-builder-form"
import { CoverLetterForm, type CoverLetterData } from "@/components/cover-letter-form"
import { useCopilotAction } from "@copilotkit/react-core"

interface Message {
  id: number
  type: "user" | "assistant" | "resources" | "crisis" | "form"
  content: string
  timestamp: Date
  resources?: Resource[]
  formType?: "resume" | "cover-letter"
}

interface CopilotModalProps {
  isOpen: boolean
  onClose: () => void
}

export function CopilotModal({ isOpen, onClose }: CopilotModalProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 1,
      type: "assistant",
      content:
        "Hi! I'm Sybl, your helpful AI assistant. What would you like help with today?",
      timestamp: new Date(),
    },
  ])
  const [inputValue, setInputValue] = useState("")
  const [isTyping, setIsTyping] = useState(false)
  const [activeForm, setActiveForm] = useState<"resume" | "cover-letter" | null>(null)
  const [resumeData, setResumeData] = useState<ResumeData | null>(null)

  // CopilotKit Actions
  useCopilotAction({
    name: "show_resume_builder",
    description: "Show the resume builder form to help user create a professional resume",
    parameters: [
      {
        name: "prefill_data",
        type: "object",
        description: "Any information already gathered from the user to prefill the form",
        required: false,
      },
    ],
    handler: async ({ prefill_data }) => {
      if (!resumeData) {
        setResumeData({
          jobContext: {
            jobTitle: "",
            companyName: "",
            jobDescription: "",
          },
          personalInfo: {
            fullName: "",
            email: "",
            phone: "",
            address: "",
            city: "",
            state: "OR",
            zipCode: "",
            linkedIn: "",
            website: "",
          },
          summary: "",
          workExperience: [],
          education: [],
          skills: [],
          certifications: [],
          achievements: [],
          ...(prefill_data || {}),
        })
      }

      const formMessage: Message = {
        id: Date.now(),
        type: "form",
        content: "I'll help you build a professional resume. Let's start with the resume builder:",
        timestamp: new Date(),
        formType: "resume",
      }
      setMessages((prev) => [...prev, formMessage])
      setActiveForm("resume")
      return "Resume builder form is now displayed. I can help guide you through each section."
    },
  })

  useCopilotAction({
    name: "update_resume_data",
    description:
      "Update the user's resume data based on the conversation. Use this to fill out or modify sections of the resume form.",
    parameters: [
      {
        name: "section",
        type: "string",
        description:
          "The section of the resume to update (e.g., 'personalInfo', 'summary', 'workExperience', 'education', 'skills').",
        required: true,
      },
      {
        name: "data",
        type: "object",
        description: "A JSON object with the fields and values to update.",
        required: true,
      },
      {
        name: "itemId",
        type: "string",
        description: "The ID of an item to update in a list section (e.g., a specific job in workExperience).",
        required: false,
      },
      {
        name: "action",
        type: "string",
        enum: ["add", "update", "remove"],
        description:
          "The action to perform on a list section: 'add' a new item, 'update' an existing one, or 'remove' one.",
        required: false,
      },
    ],
    handler: async ({ section, data, itemId, action = "update" }) => {
      if (!resumeData) {
        return "Please open the resume builder first by asking me to 'build a resume'."
      }

      setResumeData((prevData) => {
        if (!prevData) return null
        const newData = JSON.parse(JSON.stringify(prevData)) // Deep copy

        switch (section) {
          case "personalInfo":
            newData.personalInfo = { ...newData.personalInfo, ...data }
            break
          case "summary":
            newData.summary = data.summary || newData.summary
            break
          case "workExperience":
          case "education":
          case "skills":
            if (action === "add") {
              const newItem = { id: Date.now().toString(), ...data }
              newData[section].push(newItem)
            } else if (action === "update" && itemId) {
              const itemIndex = newData[section].findIndex((item: any) => item.id === itemId)
              if (itemIndex !== -1) {
                newData[section][itemIndex] = { ...newData[section][itemIndex], ...data }
              }
            } else if (action === "remove" && itemId) {
              newData[section] = newData[section].filter((item: any) => item.id !== itemId)
            }
            break
        }
        return newData
      })

      return `Successfully performed '${action}' on the '${section}' section of the resume.`
    },
  })

  useCopilotAction({
    name: "show_cover_letter_builder",
    description: "Show the cover letter builder form to help user create a personalized cover letter",
    parameters: [
      {
        name: "job_title",
        type: "string",
        description: "The job title they're applying for",
        required: false,
      },
      {
        name: "company_name",
        type: "string",
        description: "The company name they're applying to",
        required: false,
      },
    ],
    handler: async ({ job_title, company_name }) => {
      const formMessage: Message = {
        id: Date.now(),
        type: "form",
        content: "I'll help you create a compelling cover letter. Here's the cover letter builder:",
        timestamp: new Date(),
        formType: "cover-letter",
      }
      setMessages((prev) => [...prev, formMessage])
      setActiveForm("cover-letter")
      return "Cover letter builder form is now displayed. I can help you craft compelling content for each section."
    },
  })

  useCopilotAction({
    name: "search_local_resources",
    description: "Search for local Oregon resources and services based on user needs",
    parameters: [
      {
        name: "serviceType",
        type: "string",
        description: "Type of service needed (e.g., 'mental health', 'job search', 'housing', 'food assistance')",
        required: true,
      },
      {
        name: "urgency",
        type: "string",
        description: "Urgency level: high for crisis, medium for soon-needed help, low for planning",
        required: false,
      },
    ],
    handler: async ({ serviceType, urgency }) => {
      const resources = searchResources({
        serviceType,
        urgency: urgency as "low" | "medium" | "high",
      })

      if (resources.length > 0) {
        const resourceMessage: Message = {
          id: Date.now(),
          type: "resources",
          content: `I found ${resources.length} local resources that can help with ${serviceType}:`,
          timestamp: new Date(),
          resources,
        }
        setMessages((prev) => [...prev, resourceMessage])
        return `Found ${resources.length} resources for ${serviceType}`
      } else {
        return `No specific resources found for ${serviceType}, but 211info can provide comprehensive resource information.`
      }
    },
  })

  // Crisis detection
  const detectCrisis = (input: string): boolean => {
    const crisisKeywords = [
      "suicide",
      "kill myself",
      "end it all",
      "don't want to live",
      "hurt myself",
      "self harm",
      "cutting",
      "overdose",
      "jump",
      "gun",
      "pills",
      "die",
      "death",
      "hopeless",
      "can't go on",
      "no point",
      "better off dead",
    ]
    return crisisKeywords.some((keyword) => input.toLowerCase().includes(keyword))
  }

  const handleSendMessage = async () => {
    if (!inputValue.trim()) return

    const userMessage: Message = {
      id: Date.now(),
      type: "user",
      content: inputValue,
      timestamp: new Date(),
    }

    setMessages((prev) => [...prev, userMessage])
    const userInput = inputValue.toLowerCase()
    setInputValue("")
    setIsTyping(true)

    // Check for crisis situations first
    const isCrisis = detectCrisis(userInput)

    setTimeout(() => {
      if (isCrisis) {
        const crisisMessage: Message = {
          id: Date.now(),
          type: "crisis",
          content:
            "I'm really concerned about you and want to help. You're not alone in this, and there are people who care and want to support you. Please reach out for immediate help:",
          timestamp: new Date(),
        }
        setMessages((prev) => [...prev, crisisMessage])
        setIsTyping(false)
        return
      }

      // Check for resume/cover letter requests
      if (
        userInput.includes("resume") ||
        userInput.includes("cv") ||
        (userInput.includes("job") && userInput.includes("application"))
      ) {
        const formMessage: Message = {
          id: Date.now(),
          type: "form",
        if (!resumeData) {
          setResumeData({
            jobContext: {
              jobTitle: "",
              companyName: "",
              jobDescription: "",
            },
            personalInfo: {
              fullName: "",
              email: "",
              phone: "",
              address: "",
              city: "",
              state: "OR",
              zipCode: "",
              linkedIn: "",
              website: "",
            },
            summary: "",
            workExperience: [],
            education: [],
            skills: [],
            certifications: [],
            achievements: [],
          })
        }
            skills: [],
            certifications: [],
            achievements: [],
          })
        }
        setMessages((prev) => [...prev, formMessage])
        setActiveForm("resume")
        setIsTyping(false)
        return
      }

      if (userInput.includes("cover letter") || userInput.includes("application letter")) {
        const formMessage: Message = {
          id: Date.now(),
          type: "form",
          content: "I'll help you create a compelling cover letter! Here's our cover letter builder:",
          timestamp: new Date(),
          formType: "cover-letter",
        }
        setMessages((prev) => [...prev, formMessage])
        setActiveForm("cover-letter")
        setIsTyping(false)
        return
      }

      // Regular conversation
      const aiResponse: Message = {
        id: Date.now(),
        type: "assistant",
        content:
          "I'm here to help you with various needs. I can:\n\n• Help you build a professional resume\n• Create personalized cover letters\n• Find local Oregon resources for mental health, job search, housing, food assistance\n• Provide trauma-informed support and guidance\n\nWhat would be most helpful for you right now?",
        timestamp: new Date(),
      }
      setMessages((prev) => [...prev, aiResponse])
      setIsTyping(false)
    }, 1500)
  }

  const handleResumePreview = (data: ResumeData) => {
    const previewMessage: Message = {
      id: Date.now(),
      type: "assistant",
      content: `Great! I can see your resume is taking shape. You have ${data.workExperience.length} work experience entries and ${data.education.length} education entries. Would you like me to help you improve any specific sections or generate the final document?`,
      timestamp: new Date(),
    }
    setMessages((prev) => [...prev, previewMessage])
  }

  const handleResumeSave = (data: ResumeData) => {
    const saveMessage: Message = {
      id: Date.now(),
      type: "assistant",
      content: `Excellent! Your resume has been generated successfully. It includes your professional summary, ${data.workExperience.length} work experiences, education, and skills. You can download it as a PDF or Word document. Would you also like help creating a cover letter to go with your applications?`,
      timestamp: new Date(),
    }
    setMessages((prev) => [...prev, saveMessage])
    setActiveForm(null)
  }

  const handleCoverLetterSave = (data: CoverLetterData) => {
    const saveMessage: Message = {
      id: Date.now(),
      type: "assistant",
      content: `Perfect! Your cover letter for the ${data.jobTitle} position at ${data.companyName} has been created. It's personalized and professional. You can download it and use it with your job application. Good luck with your application!`,
      timestamp: new Date(),
    }
    setMessages((prev) => [...prev, saveMessage])
    setActiveForm(null)
  }

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50"
            onClick={onClose}
          />

          {/* Modal */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 20 }}
            className="fixed inset-4 md:inset-8 lg:inset-16 bg-background border border-border rounded-2xl shadow-2xl z-50 flex flex-col overflow-hidden"
          >
            {/* Header */}
            <div className="flex items-center justify-between p-6 border-b border-border bg-card/50">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-emerald-600 rounded-full flex items-center justify-center">
                  <Brain className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h2 className="text-xl font-semibold text-foreground">Sybl AI Assistant</h2>
                  <p className="text-sm text-muted-foreground">Career support • Resource finder • Resume builder</p>
                </div>
              </div>
              <Button variant="ghost" size="icon" onClick={onClose}>
                <X className="w-5 h-5" />
              </Button>
            </div>

            {/* Chat Messages */}
            <div className="flex-1 overflow-y-auto p-6 space-y-4">
              {messages.map((message) => (
                <div key={message.id} className={cn("flex", message.type === "user" ? "justify-end" : "justify-start")}>
                  <div
                    className={cn(
                      "max-w-[90%]",
                      message.type === "resources" || message.type === "form" ? "w-full" : "",
                    )}
                  >
                    {/* Crisis Messages */}
                    {message.type === "crisis" && (
                      <div className="bg-red-50 dark:bg-red-950/20 border border-red-200 dark:border-red-800 rounded-2xl px-4 py-3 mb-3">
                        <div className="flex items-start space-x-2">
                          <AlertTriangle className="w-5 h-5 text-red-600 mt-0.5 flex-shrink-0" />
                          <div>
                            <p className="text-sm text-red-800 dark:text-red-200 leading-relaxed">{message.content}</p>
                            <div className="mt-3 space-y-2">
                              <div className="bg-red-100 dark:bg-red-900/30 rounded-lg p-3">
                                <p className="text-sm font-semibold text-red-800 dark:text-red-200">Immediate Help:</p>
                                <p className="text-sm text-red-700 dark:text-red-300">
                                  • Call 988 (Suicide & Crisis Lifeline) - Available 24/7
                                </p>
                                <p className="text-sm text-red-700 dark:text-red-300">
                                  • Text "HELLO" to 741741 (Crisis Text Line)
                                </p>
                                <p className="text-sm text-red-700 dark:text-red-300">
                                  • Call 911 if you're in immediate danger
                                </p>
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                    )}

                    {/* Form Messages */}
                    {message.type === "form" && (
                      <div className="space-y-4">
                        <div className="bg-card border border-border rounded-2xl px-4 py-3">
                          <div className="flex items-center space-x-2 mb-2">
                            {message.formType === "resume" ? (
                              <User className="w-4 h-4 text-emerald-600" />
                            ) : (
                              <FileText className="w-4 h-4 text-blue-600" />
                            )}
                            <p className="text-sm font-medium text-foreground">{message.content}</p>
                          </div>
                        </div>

                        {/* Show appropriate form */}
                        {message.formType === "resume" && activeForm === "resume" && resumeData && (
                          <ResumeBuilderForm
                            resumeData={resumeData}
                            setResumeData={setResumeData}
                            onSave={handleResumeSave}
                            onPreview={handleResumePreview}
                            isVisible={true}
                          />
                        )}

                        {message.formType === "cover-letter" && activeForm === "cover-letter" && (
                          <CoverLetterForm
                            onSave={handleCoverLetterSave}
                            onPreview={(data) => console.log("Preview cover letter:", data)}
                            isVisible={true}
                          />
                        )}
                      </div>
                    )}

                    {/* Regular Messages */}
                    {message.type !== "resources" && message.type !== "crisis" && message.type !== "form" && (
                      <div
                        className={cn(
                          "rounded-2xl px-4 py-3",
                          message.type === "user"
                            ? "bg-emerald-600 text-white"
                            : "bg-card border border-border text-foreground",
                        )}
                      >
                        <p className="text-sm leading-relaxed whitespace-pre-line">{message.content}</p>
                        <p
                          className={cn(
                            "text-xs mt-2 opacity-70",
                            message.type === "user" ? "text-emerald-100" : "text-muted-foreground",
                          )}
                        >
                          {message.timestamp.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                        </p>
                      </div>
                    )}

                    {/* Resource Messages */}
                    {message.type === "resources" && (
                      <div className="space-y-3">
                        <div className="bg-card border border-border rounded-2xl px-4 py-3">
                          <div className="flex items-center space-x-2 mb-2">
                            <Search className="w-4 h-4 text-emerald-600" />
                            <p className="text-sm font-medium text-foreground">{message.content}</p>
                          </div>
                        </div>
                        {message.resources && <ResourceCarousel resources={message.resources} />}
                      </div>
                    )}
                  </div>
                </div>
              ))}

              {/* Typing Indicator */}
              {isTyping && (
                <div className="flex justify-start">
                  <div className="bg-card border border-border rounded-2xl px-4 py-3">
                    <div className="flex items-center space-x-2">
                      <div className="flex space-x-1">
                        <div className="w-2 h-2 bg-emerald-500 rounded-full animate-bounce"></div>
                        <div className="w-2 h-2 bg-emerald-500 rounded-full animate-bounce delay-100"></div>
                        <div className="w-2 h-2 bg-emerald-500 rounded-full animate-bounce delay-200"></div>
                      </div>
                      <span className="text-xs text-muted-foreground">Sybl is thinking...</span>
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Input Area */}
            <div className="p-6 border-t border-border bg-card/30">
              <div className="flex space-x-3">
                <input
                  type="text"
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  onKeyPress={(e) => e.key === "Enter" && handleSendMessage()}
                  placeholder="Ask about resume help, cover letters, job resources, or mental health support..."
                  className="flex-1 px-4 py-3 rounded-xl border border-border bg-background text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-emerald-500"
                />
                <Button
                  onClick={handleSendMessage}
                  disabled={!inputValue.trim() || isTyping}
                  className="bg-emerald-600 hover:bg-emerald-700 text-white px-6"
                >
                  Send
                </Button>
              </div>
              <p className="text-xs text-muted-foreground mt-2 text-center">
                I can help with resumes, cover letters, job search, and local Oregon resources
              </p>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  )
}

// Floating Action Button to open the modal
export function CopilotTrigger() {
  const [isModalOpen, setIsModalOpen] = useState(false)

  return (
    <>
      <motion.button
        initial={{ scale: 0 }}
        animate={{ scale: 1 }}
        whileHover={{ scale: 1.1 }}
        whileTap={{ scale: 0.95 }}
        onClick={() => setIsModalOpen(true)}
        className="fixed bottom-6 right-6 w-16 h-16 bg-emerald-600 hover:bg-emerald-700 text-white rounded-full shadow-lg flex items-center justify-center z-40 transition-colors"
      >
        <MessageCircle className="w-8 h-8" />
      </motion.button>

      <CopilotModal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} />
    </>
  )
}
