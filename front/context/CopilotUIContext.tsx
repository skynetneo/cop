'use client';

import React, { createContext, useContext, useState, ReactNode } from 'react';

// Define the shape of the context's state
interface CopilotUIContextType {
  isChatOpen: boolean;
  setIsChatOpen: (isOpen: boolean) => void;
}

// Create the context with a default undefined value
const CopilotUIContext = createContext<CopilotUIContextType | undefined>(undefined);

// Create the Provider component
export const CopilotUIProvider = ({ children }: { children: ReactNode }) => {
  const [isChatOpen, setIsChatOpen] = useState(false);

  return (
    <CopilotUIContext.Provider value={{ isChatOpen, setIsChatOpen }}>
      {children}
    </CopilotUIContext.Provider>
  );
};

// Create a custom hook for easy access to the context
export const useCustomCopilot = () => {
  const context = useContext(CopilotUIContext);
  if (context === undefined) {
    throw new Error('useCustomCopilot must be used within a CopilotUIProvider');
  }
  return context;
};