import React from "react";
import { cn } from "@/lib/utils";
import { Label } from "./label";
import { Input } from "./input"; 

interface LabelInputContainerProps {
  children: React.ReactNode;
  className?: string;
}

const LabelInputContainer = ({
  children,
  className,
}: LabelInputContainerProps) => {
  return (
    <div className={cn("flex flex-col space-y-2 w-full", className)}>
      {children}
    </div>
  );
};

export { LabelInputContainer };