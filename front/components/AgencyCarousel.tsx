import { useRouter } from "next/navigation";
import { Agency } from "@/lib/types";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Carousel, CarouselContent, CarouselItem, CarouselNext, CarouselPrevious } from "@/components/ui/carousel";

interface AgencyCarouselProps {
  categoryName: string;
  agencies: Agency[];
}

export function AgencyCarousel({ categoryName, agencies }: AgencyCarouselProps) {
  const router = useRouter();

  const handleShowOnMap = () => {
    // Encode agency data to pass in the URL query parameters
    const agenciesJson = JSON.stringify(agencies);
    const encodedAgencies = encodeURIComponent(agenciesJson);
    router.push(`/findHelp?agencies=${encodedAgencies}&category=${encodeURIComponent(categoryName)}`);
  };

  return (
    <div className="p-4 bg-gray-100 rounded-lg">
      <h3 className="text-lg font-semibold mb-2">{`Found these ${categoryName}:`}</h3>
      <Carousel className="w-full">
        <CarouselContent>
          {agencies.map((agency, index) => (
            <CarouselItem key={index} className="md:basis-1/2 lg:basis-1/3">
              <div className="p-1">
                <Card>
                  <CardHeader>
                    <CardTitle>{agency.name}</CardTitle>
                  </CardHeader>
                  <CardContent className="text-sm space-y-1">
                    <p><strong>Address:</strong> {agency.address}</p>
                    <p><strong>Contact:</strong> {agency.contactInformation || 'N/A'}</p>
                    <p><strong>Hours:</strong> {agency.hoursOfOperation || 'N/A'}</p>
                    <p><strong>Website:</strong> <a href={agency.website} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">{agency.website || 'N/A'}</a></p>
                    <p><strong>Notes:</strong> {agency.description || 'N/A'}</p>
                  </CardContent>
                </Card>
              </div>
            </CarouselItem>
          ))}
        </CarouselContent>
        <CarouselPrevious />
        <CarouselNext />
      </Carousel>
      <Button onClick={handleShowOnMap} className="mt-4 w-full">
        Map View
      </Button>
    </div>
  );
}