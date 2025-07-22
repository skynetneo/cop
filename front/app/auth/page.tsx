'use client';

import React from 'react';
import Navbar from '@/components/navbar';
import { motion } from 'framer-motion';
import { Form, FormField, FormLabel, FormControl, FormMessage } from '@/components/ui/form';
import { Input } from '@/components/ui/input';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { LabelInputContainer } from '@/components/ui/label-input';
import { BottomGradient } from '@/components/ui/bottom';
import { FormWrapperWithEffect } from '@/components/ui/form-wrapper';
// Import CopilotKit hooks
import { useCopilotAction, useCopilotReadable } from "@copilotkit/react-core";

const formSchema = z.object({
  email: z.string().email({ message: "Invalid email address." }),
  password: z.string().min(6, { message: "Password must be at least 6 characters." }),
});

const AuthPage = () => {
  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      email: "",
      password: "",
    },
  });

  // Makes the form's state readable to the AI
  useCopilotReadable({
    description: "The login/signup form fields and their current values.",
    value: form,
  });

  // Defines an action the AI can take to fill the form
  useCopilotAction({
    name: "fillAuthForm",
    description: "Fill out the login or sign-up form.",
    parameters: [
      {
        name: "email",
        type: "string",
        description: "The user's email address.",
        required: true,
      },
      {
        name: "password",
        type: "string",
        description: "The user's password. Should be at least 6 characters.",
        required: true,
      },
    ],
    handler: async ({ email, password }) => {
      // Use form.setValue to update the form fields
      form.setValue("email", email);
      form.setValue("password", password);
      return "The authentication form has been filled.";
    },
  });

  function onSubmit(values: z.infer<typeof formSchema>) {
    console.log(values);
    alert(`Attempting login/signup for ${values.email}`);
  }

  return (
    <div className="min-h-screen bg-gray-950 text-white antialiased flex flex-col">
      <Navbar />
      <main className="flex-1 flex items-center justify-center p-4 md:p-8">
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.6 }}
          className="w-full"
        >
          <FormWrapperWithEffect>
            <h2 className="text-xl font-bold text-neutral-800 dark:text-neutral-200">
              Welcome Back to Accessible Solutions!
            </h2>
            <p className="mt-2 max-w-sm text-sm text-neutral-600 dark:text-neutral-300">
              Login or Sign Up to access your personalized tools and support.
              Need help? Ask our AI assistant to fill the form for you!
            </p>

            <Form {...form}>
              <form onSubmit={form.handleSubmit(onSubmit)} className="my-8 space-y-6">
                <LabelInputContainer>
                  <FormLabel>Email Address</FormLabel>
                  <FormField
                    control={form.control}
                    name="email"
                    render={({ field }) => (
                      <FormControl>
                        <Input placeholder="your@email.com" type="email" {...field} className="bg-neutral-700 border-neutral-600 text-white" />
                      </FormControl>
                    )}
                  />
                  <FormMessage />
                </LabelInputContainer>

                <LabelInputContainer>
                  <FormLabel>Password</FormLabel>
                  <FormField
                    control={form.control}
                    name="password"
                    render={({ field }) => (
                      <FormControl>
                        <Input type="password" placeholder="••••••••" {...field} className="bg-neutral-700 border-neutral-600 text-white" />
                      </FormControl>
                    )}
                  />
                  <FormMessage />
                </LabelInputContainer>

                <button
                  className="group/btn relative block h-10 w-full rounded-md bg-gradient-to-br from-black to-neutral-600 font-medium text-white shadow-[0px_1px_0px_0px_#ffffff40_inset,0px_-1px_0px_0px_#ffffff40_inset] dark:bg-zinc-800 dark:from-zinc-900 dark:to-zinc-900 dark:shadow-[0px_1px_0px_0px_#27272a_inset,0px_-1px_0px_0px_#27272a_inset]"
                  type="submit"
                >
                  Sign Up / Login →
                  <BottomGradient />
                </button>
              </form>
            </Form>
          </FormWrapperWithEffect>
        </motion.div>
      </main>
    </div>
  );
};

export default AuthPage;