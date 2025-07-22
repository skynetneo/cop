import { Button } from "@/components/ui/button";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";
import { useAgencies } from "@/lib/hooks/use-agencies";
import { Plus, MapPin } from "lucide-react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { useState } from "react";
import { Map, Marker } from "leaflet";
import { AgencyForm } from "./PlaceForm";
import { Agency } from "@/lib/types";

export function AddAgency({ map }: { map: Map }) {
  // Get context values (addAgency and selectedAgency must be provided by AgenciesContext)
  const { selectedCategoryId, categories } = useAgencies();
  // Find selected agency/category if needed
  const selectedCategory = categories.find(cat => cat.id === selectedCategoryId) || null;

  // You may want to manage agencies at a higher level, but for now, let's assume you add to the selected category
  // Add an addAgency function to AgenciesContextType and provider if you want to mutate state here

  const [open, setOpen] = useState(false);
  const [marker, setMarker] = useState<Marker | null>(null);
  const [position, setPosition] = useState<[number, number] | null>(null);
  const [isPlacing, setIsPlacing] = useState(false);

  // If no category is selected, don't show the button
  if (!selectedCategory) return null;

  const handleStartPlacing = () => {
    setIsPlacing(true);
    map.getContainer().style.cursor = 'crosshair';

    const clickHandler = (e: any) => {
      const latlng = e.latlng;
      if (marker) {
        marker.remove();
      }
      const newMarker = new Marker(latlng).addTo(map);
      setMarker(newMarker);
      setPosition([latlng.lat, latlng.lng]);
      map.getContainer().style.cursor = '';
      map.off('click', clickHandler);
      setIsPlacing(false);
      setOpen(true);
    };

    map.on('click', clickHandler);
  };

  const handleStopPlacing = () => {
    setIsPlacing(false);
    map.getContainer().style.cursor = '';
  };

  // You need to implement addAgency in your context/provider for this to work!
  const handleAddAgency = (place: Agency) => {
    if (!position || !selectedCategory) return;

    const [latitude, longitude] = position;
    const newPlace = {
      ...place,
      latitude,
      longitude,
    };

    // This should update your context/provider state
    // Example: selectedCategory.agencies.push(newPlace);
    // Ideally, use a context function: addAgency(newPlace, selectedCategory.id);

    setOpen(false);
    setPosition(null);
    if (marker) {
      marker.remove();
      setMarker(null);
    }
  };

  return (
    <>
      <Tooltip delayDuration={0}>
        <TooltipTrigger asChild>
          <Button
            size="icon"
            className={`bg-white text-black hover:bg-white/80 ring-2 ring-border shadow-xl border-black rounded-full ${isPlacing ? 'ring-2 ring-primary' : ''}`}
            onClick={isPlacing ? handleStopPlacing : handleStartPlacing}
          >
            {isPlacing ? <MapPin className="w-4 h-4" /> : <Plus className="w-4 h-4" />}
          </Button>
        </TooltipTrigger>
        <TooltipContent side="left">
          {isPlacing ? 'Click on map to place marker' : 'Add a place'}
        </TooltipContent>
      </Tooltip>

      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle className="flex items-center">
              <Plus className="w-4 h-4 mr-2" />
              Add a New Place
            </DialogTitle>
          </DialogHeader>
          <AgencyForm
            onSubmit={handleAddAgency}
          />
        </DialogContent>
      </Dialog>
    </>
  );
}