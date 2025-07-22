"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Label } from "@/components/ui/label"
import { Plus, Download, Eye, User, Briefcase, GraduationCap, Award, FileText, Trash2, Target } from "lucide-react"
import { motion, AnimatePresence } from "framer-motion"
import { cn } from "@/lib/utils"
import { CopilotTextarea } from "@copilotkit/react-textarea"

export interface PersonalInfo {
  fullName: string
  email: string
  phone: string
  address: string
  city: string
  state: string
  zipCode: string
  linkedIn?: string
  website?: string
}

export interface WorkExperience {
  id: string
  jobTitle: string
  company: string
  location: string
  startDate: string
  endDate: string
  isCurrentJob: boolean
  responsibilities: string[]
}

export interface Education {
  id: string
  degree: string
  school: string
  location: string
  graduationDate: string
  gpa?: string
  relevantCoursework?: string
}

export interface Skill {
  id: string
  category: string
  skills: string[]
}

export interface JobContext {
  jobTitle: string
  companyName: string
  jobDescription: string
}

export interface ResumeData {
  jobContext: JobContext
  personalInfo: PersonalInfo
  education: Education[]
  workExperience: WorkExperience[]
  summary: string
  skills: Skill[]
  certifications: string[]
  achievements: string[]
}

interface ResumeBuilderFormProps {
  resumeData: ResumeData
  setResumeData: (data: ResumeData) => void
  onSave: (data: ResumeData) => void
  onPreview: (data: ResumeData) => void
  isVisible: boolean
}

export function ResumeBuilderForm({ resumeData, setResumeData, onSave, onPreview, isVisible }: ResumeBuilderFormProps) {
  const [currentStep, setCurrentStep] = useState(0)

  const steps = [
    { title: "Job Target", icon: Target },
    { title: "Personal Info", icon: User },
    { title: "Education", icon: GraduationCap },
    { title: "Work Experience", icon: Briefcase },
    { title: "Summary", icon: FileText },
    { title: "Skills", icon: Award },
  ]

  const handleUpdate = (updateFn: (draft: ResumeData) => void) => {
    const newDraft = JSON.parse(JSON.stringify(resumeData))
    updateFn(newDraft)
    setResumeData(newDraft)
  }

  const addWorkExperience = () => {
    handleUpdate((draft) => {
      draft.workExperience.push({
        id: Date.now().toString(),
        jobTitle: "",
        company: "",
        location: "",
        startDate: "",
        endDate: "",
        isCurrentJob: false,
        responsibilities: [""],
      })
    })
  }

  const removeWorkExperience = (id: string) => {
    handleUpdate((draft) => {
      draft.workExperience = draft.workExperience.filter((exp) => exp.id !== id)
    })
  }

  const addEducation = () => {
    handleUpdate((draft) => {
      draft.education.push({
        id: Date.now().toString(),
        degree: "",
        school: "",
        location: "",
        graduationDate: "",
        gpa: "",
        relevantCoursework: "",
      })
    })
  }

  const removeEducation = (id: string) => {
    handleUpdate((draft) => {
      draft.education = draft.education.filter((edu) => edu.id !== id)
    })
  }

  const addSkillCategory = () => {
    handleUpdate((draft) => {
      draft.skills.push({
        id: Date.now().toString(),
        category: "",
        skills: [""],
      })
    })
  }

  const removeSkillCategory = (id: string) => {
    handleUpdate((draft) => {
      draft.skills = draft.skills.filter((skill) => skill.id !== id)
    })
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
      <div className="bg-emerald-50 dark:bg-emerald-950/20 p-6 border-b border-border">
        <h2 className="text-2xl font-bold text-foreground mb-2">Resume Builder</h2>
        <p className="text-muted-foreground">
          {currentStep === 0
            ? "First, tell me about the job you're targeting"
            : `Building your resume for: ${resumeData.jobContext.jobTitle || "your target position"}`}
        </p>

        {/* Progress Steps */}
        <div className="flex items-center justify-between mt-6 overflow-x-auto">
          {steps.map((step, index) => (
            <div key={index} className="flex items-center flex-shrink-0">
              <div
                className={cn(
                  "w-10 h-10 rounded-full flex items-center justify-center border-2 transition-colors",
                  index <= currentStep
                    ? "bg-emerald-600 border-emerald-600 text-white"
                    : "bg-background border-muted text-muted-foreground",
                )}
              >
                <step.icon className="w-5 h-5" />
              </div>
              <span
                className={cn(
                  "ml-2 text-sm font-medium whitespace-nowrap",
                  index <= currentStep ? "text-emerald-600" : "text-muted-foreground",
                )}
              >
                {step.title}
              </span>
              {index < steps.length - 1 && (
                <div className={cn("w-8 h-0.5 mx-4", index < currentStep ? "bg-emerald-600" : "bg-muted")} />
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Form Content */}
      <div className="p-6 max-h-96 overflow-y-auto">
        <AnimatePresence mode="wait">
          {/* Step 0: Job Target */}
          {currentStep === 0 && (
            <motion.div
              key="job-target"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              className="space-y-4"
            >
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="jobTitle">Job Title *</Label>
                  <Input
                    id="jobTitle"
                    value={resumeData.jobContext.jobTitle}
                    onChange={(e) => handleUpdate((d) => (d.jobContext.jobTitle = e.target.value))}
                    placeholder="Software Developer"
                  />
                </div>
                <div>
                  <Label htmlFor="companyName">Company Name</Label>
                  <Input
                    id="companyName"
                    value={resumeData.jobContext.companyName}
                    onChange={(e) => handleUpdate((d) => (d.jobContext.companyName = e.target.value))}
                    placeholder="Tech Company Inc."
                  />
                </div>
              </div>
              <div>
                <Label htmlFor="jobDescription">Job Description</Label>
                <Textarea
                  id="jobDescription"
                  value={resumeData.jobContext.jobDescription}
                  onChange={(e) => handleUpdate((d) => (d.jobContext.jobDescription = e.target.value))}
                  placeholder="Paste the full job description here. This will help me tailor your resume to match the requirements..."
                  rows={8}
                  className="resize-none"
                />
                <p className="text-xs text-muted-foreground mt-1">
                  💡 Tip: The more detailed the job description, the better I can tailor your resume
                </p>
              </div>
            </motion.div>
          )}

          {/* Step 1: Personal Information */}
          {currentStep === 1 && (
            <motion.div
              key="personal"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              className="space-y-4"
            >
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="fullName">Full Name *</Label>
                  <Input
                    id="fullName"
                    value={resumeData.personalInfo.fullName}
                    onChange={(e) => handleUpdate((d) => (d.personalInfo.fullName = e.target.value))}
                    placeholder="John Doe"
                  />
                </div>
                <div>
                  <Label htmlFor="email">Email *</Label>
                  <Input
                    id="email"
                    type="email"
                    value={resumeData.personalInfo.email}
                    onChange={(e) => handleUpdate((d) => (d.personalInfo.email = e.target.value))}
                    placeholder="john@example.com"
                  />
                </div>
                <div>
                  <Label htmlFor="phone">Phone *</Label>
                  <Input
                    id="phone"
                    value={resumeData.personalInfo.phone}
                    onChange={(e) => handleUpdate((d) => (d.personalInfo.phone = e.target.value))}
                    placeholder="(555) 123-4567"
                  />
                </div>
                <div>
                  <Label htmlFor="address">Address</Label>
                  <Input
                    id="address"
                    value={resumeData.personalInfo.address}
                    onChange={(e) => handleUpdate((d) => (d.personalInfo.address = e.target.value))}
                    placeholder="123 Main St"
                  />
                </div>
                <div>
                  <Label htmlFor="city">City</Label>
                  <Input
                    id="city"
                    value={resumeData.personalInfo.city}
                    onChange={(e) => handleUpdate((d) => (d.personalInfo.city = e.target.value))}
                    placeholder="Portland"
                  />
                </div>
                <div>
                  <Label htmlFor="zipCode">ZIP Code</Label>
                  <Input
                    id="zipCode"
                    value={resumeData.personalInfo.zipCode}
                    onChange={(e) => handleUpdate((d) => (d.personalInfo.zipCode = e.target.value))}
                    placeholder="97201"
                  />
                </div>
                <div>
                  <Label htmlFor="linkedIn">LinkedIn (optional)</Label>
                  <Input
                    id="linkedIn"
                    value={resumeData.personalInfo.linkedIn || ""}
                    onChange={(e) => handleUpdate((d) => (d.personalInfo.linkedIn = e.target.value))}
                    placeholder="linkedin.com/in/johndoe"
                  />
                </div>
                <div>
                  <Label htmlFor="website">Website/Portfolio (optional)</Label>
                  <Input
                    id="website"
                    value={resumeData.personalInfo.website || ""}
                    onChange={(e) => handleUpdate((d) => (d.personalInfo.website = e.target.value))}
                    placeholder="johndoe.com"
                  />
                </div>
              </div>
            </motion.div>
          )}

          {/* Step 2: Education */}
          {currentStep === 2 && (
            <motion.div
              key="education"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              className="space-y-4"
            >
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold">Education</h3>
                <Button onClick={addEducation} size="sm" variant="outline">
                  <Plus className="w-4 h-4 mr-1" />
                  Add Education
                </Button>
              </div>

              {resumeData.education.map((edu, index) => (
                <Card key={edu.id} className="border border-border">
                  <CardContent className="p-4 space-y-3">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                      <Input
                        placeholder="Degree/Certification"
                        value={edu.degree}
                        onChange={(e) => handleUpdate((d) => (d.education[index].degree = e.target.value))}
                      />
                      <Input
                        placeholder="School/Institution"
                        value={edu.school}
                        onChange={(e) => handleUpdate((d) => (d.education[index].school = e.target.value))}
                      />
                      <Input
                        placeholder="Location"
                        value={edu.location}
                        onChange={(e) => handleUpdate((d) => (d.education[index].location = e.target.value))}
                      />
                      <Input
                        placeholder="Graduation Date (MM/YYYY)"
                        value={edu.graduationDate}
                        onChange={(e) => handleUpdate((d) => (d.education[index].graduationDate = e.target.value))}
                      />
                    </div>
                    <div className="flex justify-end">
                      <Button variant="ghost" size="sm" onClick={() => removeEducation(edu.id)}>
                        <Trash2 className="w-4 h-4 mr-1" />
                        Remove
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}

              {resumeData.education.length === 0 && (
                <div className="text-center py-8 text-muted-foreground">
                  <GraduationCap className="w-12 h-12 mx-auto mb-2 opacity-50" />
                  <p>No education added yet</p>
                  <p className="text-sm">Click "Add Education" to get started</p>
                </div>
              )}
            </motion.div>
          )}

          {/* Step 3: Work Experience */}
          {currentStep === 3 && (
            <motion.div
              key="experience"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              className="space-y-4"
            >
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold">Work Experience</h3>
                <Button onClick={addWorkExperience} size="sm" variant="outline">
                  <Plus className="w-4 h-4 mr-1" />
                  Add Job
                </Button>
              </div>

              {resumeData.workExperience.map((exp, index) => (
                <Card key={exp.id} className="border border-border">
                  <CardContent className="p-4 space-y-3">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                      <Input
                        placeholder="Job Title"
                        value={exp.jobTitle}
                        onChange={(e) => handleUpdate((d) => (d.workExperience[index].jobTitle = e.target.value))}
                      />
                      <Input
                        placeholder="Company Name"
                        value={exp.company}
                        onChange={(e) => handleUpdate((d) => (d.workExperience[index].company = e.target.value))}
                      />
                      <Input
                        placeholder="Location"
                        value={exp.location}
                        onChange={(e) => handleUpdate((d) => (d.workExperience[index].location = e.target.value))}
                      />
                      <div className="flex items-center space-x-2">
                        <Input
                          placeholder="Start Date (MM/YYYY)"
                          value={exp.startDate}
                          onChange={(e) => handleUpdate((d) => (d.workExperience[index].startDate = e.target.value))}
                          className="flex-1"
                        />
                        <span className="text-muted-foreground">to</span>
                        <Input
                          placeholder="End Date (MM/YYYY)"
                          value={exp.endDate}
                          onChange={(e) => handleUpdate((d) => (d.workExperience[index].endDate = e.target.value))}
                          disabled={exp.isCurrentJob}
                          className="flex-1"
                        />
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <input
                        type="checkbox"
                        id={`current-${exp.id}`}
                        checked={exp.isCurrentJob}
                        onChange={(e) => {
                          handleUpdate((d) => {
                            d.workExperience[index].isCurrentJob = e.target.checked
                            if (e.target.checked) {
                              d.workExperience[index].endDate = ""
                            }
                          })
                        }}
                        className="rounded"
                      />
                      <Label htmlFor={`current-${exp.id}`} className="text-sm">
                        I currently work here
                      </Label>
                    </div>
                    <div>
                      <Label>Key Responsibilities & Achievements</Label>
                      <CopilotTextarea
                        className="min-h-[100px] mt-1"
                        value={exp.responsibilities.join("\n")}
                        onValueChange={(value: string) =>
                          handleUpdate(
                            (d) =>
                              (d.workExperience[index].responsibilities = value.split("\n").filter((r) => r.trim())),
                          )
                        }
                        placeholder="• Describe your key responsibilities and achievements
• Use bullet points for better readability
• Focus on quantifiable results when possible
• Highlight skills relevant to your target job"
                        autosuggestionsConfig={{
                          textareaPurpose: `Generate professional bullet points for a ${exp.jobTitle || "your"} position at ${exp.company || "the company"}, focusing on responsibilities and achievements that align with the target job: ${resumeData.jobContext.jobTitle || "the target position"}. Include quantifiable results and relevant skills from the job description.`,
                          chatApiConfigs: {
                            suggestionsApiConfig: {
                              maxTokens: 50,
                              stop: ["\n\n", "•"],
                            },
                          },
                        }}
                      />
                    </div>
                    <div className="flex justify-end">
                      <Button variant="ghost" size="sm" onClick={() => removeWorkExperience(exp.id)}>
                        <Trash2 className="w-4 h-4 mr-1" />
                        Remove
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}

              {resumeData.workExperience.length === 0 && (
                <div className="text-center py-8 text-muted-foreground">
                  <Briefcase className="w-12 h-12 mx-auto mb-2 opacity-50" />
                  <p>No work experience added yet</p>
                  <p className="text-sm">Click "Add Job" to get started</p>
                </div>
              )}
            </motion.div>
          )}

          {/* Step 4: Professional Summary */}
          {currentStep === 4 && (
            <motion.div
              key="summary"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              className="space-y-4"
            >
              <div>
                <Label htmlFor="summary">Professional Summary</Label>
                <CopilotTextarea
                  className="min-h-[150px] mt-1"
                  value={resumeData.summary}
                  onValueChange={(value: string) => handleUpdate((d) => (d.summary = value))}
                  placeholder="Write a compelling professional summary that highlights your key qualifications and aligns with the target job..."
                  autosuggestionsConfig={{
                    textareaPurpose: `Create a professional summary for a ${resumeData.jobContext.jobTitle || "target"} position that highlights the candidate's most relevant qualifications, experience, and skills. Base this on their work history: ${resumeData.workExperience.map((exp) => `${exp.jobTitle} at ${exp.company}`).join(", ")} and education: ${resumeData.education.map((edu) => `${edu.degree} from ${edu.school}`).join(", ")}. Match the job requirements: ${resumeData.jobContext.jobDescription.substring(0, 200)}...`,
                    chatApiConfigs: {
                      suggestionsApiConfig: {
                        maxTokens: 80,
                        stop: ["\n\n"],
                      },
                    },
                  }}
                />
                <p className="text-xs text-muted-foreground mt-1">
                  This AI-powered textarea will help you craft a summary tailored to your target job
                </p>
              </div>
            </motion.div>
          )}

          {/* Step 5: Skills */}
          {currentStep === 5 && (
            <motion.div
              key="skills"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              className="space-y-4"
            >
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold">Skills</h3>
                <Button onClick={addSkillCategory} size="sm" variant="outline">
                  <Plus className="w-4 h-4 mr-1" />
                  Add Category
                </Button>
              </div>

              {resumeData.skills.map((skillGroup, index) => (
                <Card key={skillGroup.id} className="border border-border">
                  <CardContent className="p-4 space-y-3">
                    <Input
                      placeholder="Skill Category (e.g., Technical Skills, Languages)"
                      value={skillGroup.category}
                      onChange={(e) => handleUpdate((d) => (d.skills[index].category = e.target.value))}
                    />
                    <div>
                      <Label>Skills</Label>
                      <CopilotTextarea
                        className="min-h-[80px] mt-1"
                        value={skillGroup.skills.join(", ")}
                        onValueChange={(value: string) =>
                          handleUpdate(
                            (d) =>
                              (d.skills[index].skills = value
                                .split(",")
                                .map((s) => s.trim())
                                .filter((s) => s)),
                          )
                        }
                        placeholder="List relevant skills separated by commas..."
                        autosuggestionsConfig={{
                          textareaPurpose: `Generate a comprehensive list of ${skillGroup.category || "relevant"} skills for a ${resumeData.jobContext.jobTitle || "target"} position. Base suggestions on the job requirements: ${resumeData.jobContext.jobDescription.substring(0, 300)}... and the candidate's background in: ${resumeData.workExperience.map((exp) => exp.jobTitle).join(", ")}. Include both technical and soft skills as appropriate.`,
                          chatApiConfigs: {
                            suggestionsApiConfig: {
                              maxTokens: 40,
                              stop: ["\n", "."],
                            },
                          },
                        }}
                      />
                    </div>
                    <div className="flex justify-end">
                      <Button variant="ghost" size="sm" onClick={() => removeSkillCategory(skillGroup.id)}>
                        <Trash2 className="w-4 h-4 mr-1" />
                        Remove
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}

              {resumeData.skills.length === 0 && (
                <div className="text-center py-8 text-muted-foreground">
                  <Award className="w-12 h-12 mx-auto mb-2 opacity-50" />
                  <p>No skills added yet</p>
                  <p className="text-sm">Click "Add Category" to get started</p>
                </div>
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Footer */}
      <div className="p-6 border-t border-border bg-muted/30 flex items-center justify-between">
        <div className="flex space-x-2">
          <Button
            variant="outline"
            onClick={() => setCurrentStep(Math.max(0, currentStep - 1))}
            disabled={currentStep === 0}
          >
            Previous
          </Button>
          <Button
            onClick={() => setCurrentStep(Math.min(steps.length - 1, currentStep + 1))}
            disabled={currentStep === steps.length - 1}
          >
            Next
          </Button>
        </div>

        <div className="flex space-x-2">
          <Button variant="outline" onClick={() => onPreview(resumeData)}>
            <Eye className="w-4 h-4 mr-1" />
            Preview
          </Button>
          <Button onClick={() => onSave(resumeData)} className="bg-emerald-600 hover:bg-emerald-700">
            <Download className="w-4 h-4 mr-1" />
            Generate Resume
          </Button>
        </div>
      </div>
    </motion.div>
  )
}
