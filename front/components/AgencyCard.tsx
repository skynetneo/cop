'use client';

import React, { ReactNode } from "react";
import { Card, CardTitle, CardContent } from "@/components/ui/card";
import { Agency } from "@/lib/types";
import { MapPin, Info, Phone, Globe } from "lucide-react";
import { cn } from "@/lib/utils";
import { Checkbox } from "@/components/ui/checkbox";

type AgencyCardProps = {
  agency: Agency;
  className?: string;
  number?: number;
  actions?: ReactNode;
  onMouseEnter?: () => void;
  onMouseLeave?: () => void;
  checked?: boolean;
  onCheck?: (checked: boolean) => void;
  shouldShowCheckbox?: boolean;
};

export function AgencyCard({
  agency,
  actions,
  onMouseEnter,
  onMouseLeave,
  className,
  number,
  checked,
  onCheck,
  shouldShowCheckbox = true,
}: AgencyCardProps) {
  return (
    <Card
      className={cn("hover:shadow-md transition-shadow duration-200 bg-white dark:bg-neutral-800 border-neutral-700", className)}
      onMouseEnter={onMouseEnter}
      onMouseLeave={onMouseLeave}
    >
      <CardContent className="pt-6">
        <div className="space-y-4">
          <div className="flex justify-between items-start">
            <div className="space-y-2">
              <CardTitle className="text-xl font-semibold flex items-center gap-2 text-black dark:text-white">
                {number && (
                  <div className="text-sm text-white bg-black dark:bg-white dark:text-black rounded-full flex items-center justify-center font-bold border-2 border-white w-7 h-7">
                    {number}
                  </div>
                )}
                {agency.name}
              </CardTitle>
              <p className="text-sm text-blue-500 dark:text-blue-400 font-medium">{agency.category}</p>
            </div>
            <div className="flex flex-col items-end gap-2 min-w-[2rem]">
              {actions}
              {shouldShowCheckbox && (
                <Checkbox
                  checked={checked}
                  onCheckedChange={onCheck as (checked: boolean | 'indeterminate') => void}
                />
              )}
            </div>
          </div>

          <div className="space-y-2 text-sm text-neutral-600 dark:text-neutral-300">
            {agency.description && (
              <div className="flex items-start gap-2 pt-2">
                <Info className="w-4 h-4 mt-0.5 shrink-0" />
                <p className="flex-1">{agency.description}</p>
              </div>
            )}
            {agency.address && (
              <div className="flex items-start gap-2">
                <MapPin className="w-4 h-4 mt-0.5 shrink-0" />
                <span>{Array.isArray(agency.address) ? agency.address.join(', ') : agency.address}</span>
              </div>
            )}
            {agency.contactInformation?.map((contact, i) => (
                <div key={i} className="flex items-start gap-2">
                    {contact.includes('http') ? <Globe className="w-4 h-4 mt-0.5 shrink-0" /> : <Phone className="w-4 h-4 mt-0.5 shrink-0" />}
                    <a href={contact.includes('http') ? contact : `tel:${contact}`} target="_blank" rel="noopener noreferrer" className="hover:underline">
                        {contact}
                    </a>
                </div>
            ))}
            {agency.hoursOfOperation && (
                <div className="flex items-start gap-2">
                    <p className="font-semibold">Hours:</p>
                    <p className="flex-1">{agency.hoursOfOperation}</p>
                </div>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}