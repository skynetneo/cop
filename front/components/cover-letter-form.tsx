"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { FileText, Download, Eye } from "lucide-react"
import { motion } from "framer-motion"
import { CopilotTextarea } from "@copilotkit/react-textarea"

export interface CoverLetterData {
  jobTitle: string
  companyName: string
  hiringManagerName: string
  companyAddress: string
  introduction: string
  bodyParagraph1: string
  bodyParagraph2: string
  closing: string
  applicantName: string
  applicantSignature: string
}

interface CoverLetterFormProps {
  onSave: (data: CoverLetterData) => void
  onPreview: (data: CoverLetterData) => void
  initialData?: Partial<CoverLetterData>
  isVisible: boolean
  jobContext?: {
    jobTitle: string
    companyName: string
    jobDescription: string
    keywords?: string[]
  }
  resumeContext?: {
    personalInfo: {
      fullName: string
      email: string
      phone: string
    }
    workExperience: Array<{
      jobTitle: string
      company: string
      responsibilities: string[]
    }>
    education: Array<{
      degree: string
      school: string
    }>
    skills: Array<{
      category: string
      skills: string[]
    }>
    summary: string
  }
}

export function CoverLetterForm({
  onSave,
  onPreview,
  initialData,
  isVisible,
  jobContext,
  resumeContext,
}: CoverLetterFormProps) {
  const [formData, setFormData] = useState<CoverLetterData>({
    jobTitle: jobContext?.jobTitle || "",
    companyName: jobContext?.companyName || "",
    hiringManagerName: "",
    companyAddress: "",
    introduction: "",
    bodyParagraph1: "",
    bodyParagraph2: "",
    closing: "",
    applicantName: resumeContext?.personalInfo?.fullName || "",
    applicantSignature: "",
    ...initialData,
  })

  const updateField = (field: keyof CoverLetterData, value: string) => {
    setFormData((prev) => ({ ...prev, [field]: value }))
  }

  // Generate context string for AI assistance
  const getContextString = () => {
    let context = ""

    if (jobContext) {
      context += `Job Target: ${jobContext.jobTitle} at ${jobContext.companyName}\n`
      if (jobContext.jobDescription) {
        context += `Job Description: ${jobContext.jobDescription}\n\n`
      }
      if (jobContext.keywords && jobContext.keywords.length > 0) {
        context += `Key Requirements: ${jobContext.keywords.join(", ")}\n\n`
      }
    }

    if (resumeContext) {
      context += `Candidate Profile:\n`
      context += `Name: ${resumeContext.personalInfo.fullName}\n`

      if (resumeContext.summary) {
        context += `Professional Summary: ${resumeContext.summary}\n\n`
      }

      if (resumeContext.workExperience.length > 0) {
        context += "Work Experience:\n"
        resumeContext.workExperience.forEach((exp) => {
          context += `- ${exp.jobTitle} at ${exp.company}\n`
          if (exp.responsibilities.length > 0) {
            context += `  Key achievements: ${exp.responsibilities.slice(0, 2).join("; ")}\n`
          }
        })
        context += "\n"
      }

      if (resumeContext.education.length > 0) {
        context += "Education:\n"
        resumeContext.education.forEach((edu) => {
          context += `- ${edu.degree} from ${edu.school}\n`
        })
        context += "\n"
      }

      if (resumeContext.skills.length > 0) {
        context += "Key Skills:\n"
        resumeContext.skills.forEach((skillGroup) => {
          context += `- ${skillGroup.category}: ${skillGroup.skills.slice(0, 5).join(", ")}\n`
        })
      }
    }

    return context
  }

  if (!isVisible) return null

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="w-full max-w-4xl mx-auto bg-background border border-border rounded-2xl shadow-lg overflow-hidden"
    >
      {/* Header */}
      <div className="bg-blue-50 dark:bg-blue-950/20 p-6 border-b border-border">
        <div className="flex items-center space-x-3">
          <FileText className="w-8 h-8 text-blue-600" />
          <div>
            <h2 className="text-2xl font-bold text-foreground">Cover Letter Builder</h2>
            <p className="text-muted-foreground">
              {jobContext
                ? `Creating a personalized cover letter for ${jobContext.jobTitle} at ${jobContext.companyName}`
                : "Create a personalized cover letter for your application"}
            </p>
          </div>
        </div>
      </div>

      {/* Form Content */}
      <div className="p-6 max-h-96 overflow-y-auto space-y-6">
        {/* Job & Company Information */}
        <Card>
          <CardContent className="p-4 space-y-4">
            <h3 className="font-semibold text-foreground">Job & Company Details</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <Label htmlFor="jobTitle">Job Title *</Label>
                <Input
                  id="jobTitle"
                  value={formData.jobTitle}
                  onChange={(e) => updateField("jobTitle", e.target.value)}
                  placeholder="Software Developer"
                />
              </div>
              <div>
                <Label htmlFor="companyName">Company Name *</Label>
                <Input
                  id="companyName"
                  value={formData.companyName}
                  onChange={(e) => updateField("companyName", e.target.value)}
                  placeholder="Tech Company Inc."
                />
              </div>
              <div>
                <Label htmlFor="hiringManagerName">Hiring Manager Name</Label>
                <Input
                  id="hiringManagerName"
                  value={formData.hiringManagerName}
                  onChange={(e) => updateField("hiringManagerName", e.target.value)}
                  placeholder="Jane Smith (optional)"
                />
              </div>
              <div>
                <Label htmlFor="companyAddress">Company Address</Label>
                <Input
                  id="companyAddress"
                  value={formData.companyAddress}
                  onChange={(e) => updateField("companyAddress", e.target.value)}
                  placeholder="123 Business St, Portland, OR"
                />
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Letter Content */}
        <Card>
          <CardContent className="p-4 space-y-4">
            <h3 className="font-semibold text-foreground">Letter Content</h3>

            <div>
              <Label htmlFor="introduction">Opening Paragraph *</Label>
              <CopilotTextarea
                className="min-h-[100px] mt-1"
                value={formData.introduction}
                onValueChange={(value: string) => updateField("introduction", value)}
                placeholder="Express your interest in the position and briefly mention how you learned about it..."
                autosuggestionsConfig={{
                  textareaPurpose: `Write a compelling opening paragraph for a cover letter applying for the ${formData.jobTitle} position at ${formData.companyName}. Express genuine interest in the role and company, and briefly introduce the candidate's most relevant qualification. Make it engaging and personalized.`,
                  chatApiConfigs: {
                    suggestionsApiConfig: {
                      maxTokens: 60,
                      stop: ["\n\n"],
                    },
                  },
                }}
              />
              <p className="text-xs text-muted-foreground mt-1">
                💡 AI will help craft an engaging opening that connects you to the role
              </p>
            </div>

            <div>
              <Label htmlFor="bodyParagraph1">Body Paragraph 1 - Your Qualifications *</Label>
              <CopilotTextarea
                className="min-h-[120px] mt-1"
                value={formData.bodyParagraph1}
                onValueChange={(value: string) => updateField("bodyParagraph1", value)}
                placeholder="Highlight your relevant experience, skills, and achievements that make you a strong candidate..."
                autosuggestionsConfig={{
                  textareaPurpose: `Write a compelling body paragraph that highlights the candidate's most relevant qualifications for the ${formData.jobTitle} position. Focus on specific experiences, skills, and achievements that directly align with the job requirements. Use concrete examples and quantifiable results where possible. Context: ${getContextString()}`,
                  chatApiConfigs: {
                    suggestionsApiConfig: {
                      maxTokens: 80,
                      stop: ["\n\n"],
                    },
                  },
                }}
              />
              <p className="text-xs text-muted-foreground mt-1">
                💡 AI will match your experience to the job requirements
              </p>
            </div>

            <div>
              <Label htmlFor="bodyParagraph2">Body Paragraph 2 - Company Connection</Label>
              <CopilotTextarea
                className="min-h-[120px] mt-1"
                value={formData.bodyParagraph2}
                onValueChange={(value: string) => updateField("bodyParagraph2", value)}
                placeholder="Explain why you're interested in this company and how you can contribute to their goals..."
                autosuggestionsConfig={{
                  textareaPurpose: `Write a paragraph that demonstrates the candidate's knowledge of and enthusiasm for ${formData.companyName}. Explain why they want to work specifically for this company and how their skills and experience can contribute to the company's goals and success. Make it genuine and specific to the company and role.`,
                  chatApiConfigs: {
                    suggestionsApiConfig: {
                      maxTokens: 70,
                      stop: ["\n\n"],
                    },
                  },
                }}
              />
              <p className="text-xs text-muted-foreground mt-1">
                💡 AI will help you connect with the company's mission and values
              </p>
            </div>

            <div>
              <Label htmlFor="closing">Closing Paragraph *</Label>
              <CopilotTextarea
                className="min-h-[80px] mt-1"
                value={formData.closing}
                onValueChange={(value: string) => updateField("closing", value)}
                placeholder="Thank them for their consideration and express your interest in discussing the opportunity further..."
                autosuggestionsConfig={{
                  textareaPurpose: `Write a professional closing paragraph that thanks the hiring manager for their consideration, reiterates interest in the ${formData.jobTitle} position, and includes a call to action for next steps (interview, discussion, etc.). Keep it confident but respectful.`,
                  chatApiConfigs: {
                    suggestionsApiConfig: {
                      maxTokens: 50,
                      stop: ["\n\n"],
                    },
                  },
                }}
              />
              <p className="text-xs text-muted-foreground mt-1">💡 AI will create a strong, professional closing</p>
            </div>
          </CardContent>
        </Card>

        {/* Signature */}
        <Card>
          <CardContent className="p-4 space-y-4">
            <h3 className="font-semibold text-foreground">Signature</h3>
            <div>
              <Label htmlFor="applicantName">Your Full Name *</Label>
              <Input
                id="applicantName"
                value={formData.applicantName}
                onChange={(e) => updateField("applicantName", e.target.value)}
                placeholder="John Doe"
              />
            </div>
          </CardContent>
        </Card>

        {/* Context Preview (for debugging/transparency) */}
        {(jobContext || resumeContext) && (
          <Card className="bg-muted/30">
            <CardContent className="p-4">
              <h3 className="font-semibold text-foreground mb-2">AI Context Preview</h3>
              <div className="text-xs text-muted-foreground space-y-1">
                {jobContext && (
                  <p>
                    ✅ Job context: {jobContext.jobTitle} at {jobContext.companyName}
                  </p>
                )}
                {resumeContext && (
                  <>
                    <p>
                      ✅ Resume data: {resumeContext.workExperience.length} jobs, {resumeContext.education.length}{" "}
                      education entries
                    </p>
                    <p>✅ Skills: {resumeContext.skills.length} categories</p>
                  </>
                )}
                <p className="text-emerald-600">💡 AI will use this context to personalize your cover letter</p>
              </div>
            </CardContent>
          </Card>
        )}
      </div>

      {/* Footer */}
      <div className="p-6 border-t border-border bg-muted/30 flex items-center justify-end space-x-2">
        <Button variant="outline" onClick={() => onPreview(formData)}>
          <Eye className="w-4 h-4 mr-1" />
          Preview
        </Button>
        <Button onClick={() => onSave(formData)} className="bg-blue-600 hover:bg-blue-700">
          <Download className="w-4 h-4 mr-1" />
          Generate Cover Letter
        </Button>
      </div>
    </motion.div>
  )
}
