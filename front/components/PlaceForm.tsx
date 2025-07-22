import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Stars } from "@/components/Stars";
import { useState, useEffect } from "react";
import type { Agency } from "@/lib/types";

interface AgencyFormProps {
  onSubmit: (agency: Agency) => void;
  agency?: Agency;
  submitLabel?: string;
}

export function AgencyForm({
  onSubmit,
  agency,
  submitLabel = agency ? "Save Changes" : "Add Agency",
}: AgencyFormProps) {
  /* ---------- local state ---------- */
  const [name, setName] = useState(agency?.name ?? "");
  const [description, setDescription] = useState(agency?.description ?? "");
  const [address, setAddress] = useState(agency?.address ?? "");
  const [hoursOfOperation, setHoursOfOperation] = useState(
    agency?.hoursOfOperation ?? "",
  );
  const [contactInformation, setContactInformation] = useState<string>(
    (agency?.contactInformation ?? []).join(", "),
  );
  const [website, setWebsite] = useState(agency?.website ?? "");
  const [category, setCategory] = useState<number>(agency?.category ?? 0);
  const [hoverCategory, setHoverCategory] = useState<number | null>(null);

  /* ---------- sync when prop changes ---------- */
  useEffect(() => {
    if (agency) {
      setName(agency.name);
      setDescription(agency.description ?? "");
      setAddress(agency.address);
      setHoursOfOperation(agency.hoursOfOperation ?? "");
      setContactInformation((agency.contactInformation ?? []).join(", "));
      setWebsite(agency.website ?? "");
      setCategory(agency.category ? parseInt(agency.category, 10) : 0);
      setHoverCategory(null); 
    }
  }, [agency]);

  /* ---------- submit ---------- */
  const handleSubmit = () => {
    onSubmit({
      id: agency?.id ?? Date.now().toString(),
      name,
      description,
      address,
      hoursOfOperation,
      contactInformation: contactInformation
        .split(",")
        .map((s: string) => s.trim())
        .filter(Boolean),
      website,
      latitude: agency?.latitude ?? 0,
      longitude: agency?.longitude ?? 0,
      category: agency?.category ?? "Uncategorized", // Default category
    });
  };

  /* ---------- render ---------- */
  return (
    <div className="grid gap-4 py-4">
      {/* Name */}
      <div className="grid gap-2">
        <Label htmlFor="name">Agency name</Label>
        <Input
          id="name"
          placeholder="Enter agency name"
          value={name}
          onChange={(e) => setName(e.target.value)}
        />
      </div>

      {/* Address */}
      <div className="grid gap-2">
        <Label htmlFor="address">Address</Label>
        <Input
          id="address"
          placeholder="Enter address"
          value={address}
          onChange={(e) => setAddress(e.target.value)}
        />
      </div>

      {/* Hours */}
      <div className="grid gap-2">
        <Label htmlFor="hours">Hours of operation</Label>
        <Input
          id="hours"
          placeholder="Mon-Fri 8-5"
          value={hoursOfOperation}
          onChange={(e) => setHoursOfOperation(e.target.value)}
        />
      </div>

      {/* Website */}
      <div className="grid gap-2">
        <Label htmlFor="website">Website</Label>
        <Input
          id="website"
          placeholder="https://example.org"
          value={website}
          onChange={(e) => setWebsite(e.target.value)}
        />
      </div>

      {/* Description */}
      <div className="grid gap-2">
        <Label htmlFor="description">Description</Label>
        <Input
          id="description"
          placeholder="Short description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
        />
      </div>

      {/* Contact */}
      <div className="grid gap-2">
        <Label htmlFor="contact">Contact info (comma separated)</Label>
        <Input
          id="contact"
          placeholder="541-555-1234, info@example.org"
          value={contactInformation}
          onChange={(e) => setContactInformation(e.target.value)}
        />
      </div>

  
      <Button onClick={handleSubmit}>{submitLabel}</Button>
    </div>
  );
}