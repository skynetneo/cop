import { MapContainer, TileLayer, Marker, Tooltip } from "react-leaflet";
import { useAgencies } from "@/lib/hooks/use-agencies";
import { useEffect, useState, useRef } from "react";
import { Map, divIcon } from "leaflet";
import { cn } from "@/lib/utils";
import { TripCard } from "@/components/TripCard";
import { AgencyCard } from "@/components/AgencyCard";
import { useMediaQuery } from "@/lib/hooks/use-media-query";
import { MobileTripCard } from "./MobileTripCard";
import { useChatContext } from "@copilotkit/react-ui";

export type MapCanvasProps = {
  className?: string;
}

export function MapCanvas({ className }: MapCanvasProps) {
	const [map, setMap] = useState<Map | null>(null);
	const { selectedAgencyId } = useAgencies();
  const { setOpen } = useChatContext();
  const isDesktop = useMediaQuery("(min-width: 900px)");
  const prevIsDesktop = useRef(isDesktop);

  useEffect(() => {
    if (prevIsDesktop.current !== isDesktop) {
      setOpen(isDesktop);
    }
    prevIsDesktop.current = isDesktop;
  }, [isDesktop, setOpen]);

  return (
		<div className="">
			<MapContainer
				className={cn("w-screen h-screen", className)}
				style={{ zIndex: 0 }}
				center={[0, 0]}
				zoom={1}
				zoomAnimationThreshold={100}
				zoomControl={false}
				ref={setMap}
			>
				<TileLayer
					url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
					attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
				/>
      {selectedAgencyId && Array.isArray(selectedAgencyId) && selectedAgencyId.map((agency, i) => (
        <Marker 
          key={i} 
          position={[agency.latitude, agency.longitude]}
          icon={divIcon({
            className: "bg-transparent",
            html: `<div class="bg-foreground text-background w-8 h-8 rounded-full flex items-center justify-center font-bold border-2 border-white shadow-lg">${i + 1}</div>`,
            iconSize: [32, 32],
            iconAnchor: [16, 16],
          })}
        >
          <Tooltip offset={[10, 0]} opacity={1}>
            <AgencyCard shouldShowCheckbox={false} className="border-none overflow-y-auto shadow-none" agency={agency} />
          </Tooltip>
        </Marker>
      ))}
      </MapContainer>
      {map &&
        <>
          {isDesktop ? (
            <div className="absolute h-screen top-0 p-10 pointer-events-none flex items-start w-[30%] md:w-[50%] lg:w-[40%] 2xl:w-[35%]">
              <TripCard
                className="w-full h-full pointer-events-auto" 
                map={map} 
              />
            </div>
          ) : (
            <MobileTripCard className="w-full h-full pointer-events-auto" map={map} />
          )}
        </> 
      }
		</div>
  );
}