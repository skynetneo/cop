'use client';

import React from 'react';
import Navbar from '@/components/navbar';
import { motion } from 'framer-motion';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Form, FormField, FormLabel, FormControl, FormMessage, FormDescription } from '@/components/ui/form';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Button } from '@/components/ui/button';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { Mail, Phone, MapPin } from 'lucide-react';
import { LabelInputContainer } from '@/components/ui/label-input';
import { BottomGradient } from '@/components/ui/bottom';
import { FormWrapperWithEffect } from '@/components/ui/form-wrapper';;
// Import CopilotKit hooks
import { useCopilotAction, useCopilotReadable } from "@copilotkit/react-core";

const contactFormSchema = z.object({
  name: z.string().min(2, { message: "Name must be at least 2 characters." }),
  email: z.string().email({ message: "Invalid email address." }),
  message: z.string().min(10, { message: "Message must be at least 10 characters." }),
});

const ContactPage = () => {
  const form = useForm<z.infer<typeof contactFormSchema>>({
    resolver: zodResolver(contactFormSchema),
    defaultValues: {
      name: "",
      email: "",
      message: "",
    },
  });

  // Makes the form's state readable to the AI
  useCopilotReadable({
    description: "The contact form fields and their current values.",
    value: form,
  });

  // Defines an action the AI can take to fill the contact form
  useCopilotAction({
    name: "fillContactForm",
    description: "Fill out the contact form.",
    parameters: [
      {
        name: "name",
        type: "string",
        description: "The user's full name.",
        required: true,
      },
      {
        name: "email",
        type: "string",
        description: "The user's email address.",
        required: true,
      },
      {
        name: "message",
        type: "string",
        description: "The message the user wants to send. Should be detailed and at least 10 characters long.",
        required: true,
      },
    ],
    handler: async ({ name, email, message }) => {
      // Use form.setValue to update the form fields
      form.setValue("name", name);
      form.setValue("email", email);
      form.setValue("message", message);
      return "The contact form has been filled with your details.";
    },
  });

  function onSubmit(values: z.infer<typeof contactFormSchema>) {
    console.log(values);
    alert(`Thank you for your message, ${values.name}! We will get back to you soon.`);
    form.reset();
  }

  return (
    <div className="min-h-screen bg-gray-950 text-white antialiased flex flex-col">
      <Navbar />
      <main className="flex-1 py-20 px-4 md:px-8 max-w-7xl mx-auto">
        <motion.h1
          initial={{ opacity: 0, y: 50 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="text-5xl md:text-7xl font-extrabold text-center mb-10 text-orange-400"
        >
          Contact Us
        </motion.h1>
        
        <motion.p
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="text-lg md:text-xl text-center text-neutral-300 max-w-3xl mx-auto mb-16"
        >
          We'd love to hear from you! Reach out with any questions, feedback, or support inquiries.
          Feel free to ask our AI assistant to help you write and send your message.
        </motion.p>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 mb-20">
          <motion.div
            initial={{ opacity: 0, x: -50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6, delay: 0.4 }}
          >
            <FormWrapperWithEffect>
              <h2 className="text-xl font-bold text-neutral-800 dark:text-neutral-200 mb-4">Send us a message</h2>
              <Form {...form}>
                <form onSubmit={form.handleSubmit(onSubmit)} className="my-8 space-y-6">
                  <LabelInputContainer>
                    <FormLabel>Your Name</FormLabel>
                    <FormField control={form.control} name="name" render={({ field }) => (
                      <FormControl><Input placeholder="John Doe" {...field} className="bg-neutral-700 border-neutral-600 text-white" /></FormControl>
                    )} />
                    <FormMessage />
                  </LabelInputContainer>

                  <LabelInputContainer>
                    <FormLabel>Your Email</FormLabel>
                    <FormField control={form.control} name="email" render={({ field }) => (
                      <FormControl><Input type="email" placeholder="you@example.com" {...field} className="bg-neutral-700 border-neutral-600 text-white" /></FormControl>
                    )} />
                    <FormMessage />
                  </LabelInputContainer>

                  <LabelInputContainer>
                    <FormLabel>Message</FormLabel>
                    <FormField control={form.control} name="message" render={({ field }) => (
                      <FormControl><Textarea placeholder="How can we help you?" rows={5} {...field} className="bg-neutral-700 border-neutral-600 text-white" /></FormControl>
                    )} />
                    <FormMessage />
                  </LabelInputContainer>

                  <button
                    className="group/btn relative block h-10 w-full rounded-md bg-gradient-to-br from-black to-neutral-600 font-medium text-white shadow-[0px_1px_0px_0px_#ffffff40_inset,0px_-1px_0px_0px_#ffffff40_inset] dark:bg-zinc-800 dark:from-zinc-900 dark:to-zinc-900 dark:shadow-[0px_1px_0px_0px_#27272a_inset,0px_-1px_0px_0px_#27272a_inset]"
                    type="submit"
                  >
                    Send Message →
                    <BottomGradient />
                  </button>
                </form>
              </Form>
            </FormWrapperWithEffect>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, x: 50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6, delay: 0.5 }}
          >
            <Card className="h-full bg-neutral-800 border-neutral-700 shadow-xl flex flex-col justify-between">
              <CardHeader><CardTitle className="text-2xl text-orange-200">Our Details</CardTitle></CardHeader>
              <CardContent className="space-y-6">
                <div className="flex items-center gap-4 text-neutral-300"><Mail className="h-6 w-6 text-orange-300" /><span>info@accessiblesolutions.com</span></div>
                <div className="flex items-center gap-4 text-neutral-300"><Phone className="h-6 w-6 text-orange-300" /><span>+1 (555) 123-4567</span></div>
                <div className="flex items-start gap-4 text-neutral-300"><MapPin className="h-6 w-6 text-orange-300 shrink-0 mt-1" /><span>123 Accessible Lane, Suite 100<br/>Empowerment City, CA 90210</span></div>
              </CardContent>
            </Card>
          </motion.div>
        </div>
      </main>
    </div>
  );
};

export default ContactPage;