import { SearchProgress } from "@/components/SearchProgress";
import { useCoAgent, useCoAgentStateRender, useCopilotAction } from "@copilotkit/react-core";
import { useCopilotChatSuggestions } from "@copilotkit/react-ui";
import { createContext, useContext, ReactNode } from "react";
import { Agency, AgencyCategory, AgentState, defaultCategories } from "@/lib/types";
import { AgencyCarousel } from "@/components/AgencyCarousel";

type AgenciesContextType = {
  categories: AgencyCategory[];
  selectedCategoryId: string | null;
};

const AgenciesContext = createContext<AgenciesContextType | undefined>(undefined);

export const AgenciesProvider = ({ children }: { children: ReactNode }) => {
  const { state } = useCoAgent<AgentState>({
    name: "resource_finder",
    initialState: {
      categories: defaultCategories,
      selected_agency_id: null,
    },
  });

  useCoAgentStateRender<AgentState>({
    name: "resource_finder",
    render: ({ state }) => {
      if (state.search_progress && state.search_progress.length > 0) {
        return <SearchProgress progress={state.search_progress} />;
      }
      return null;
    },
  });

  useCopilotAction({
    name: "display_agencies",
    description: "Displays a carousel of agencies to the user.",
    parameters: [
      { name: "category_name", type: "string", description: "The name of the agency category, e.g., 'Food Banks'", required: true },
      {
        name: "agencies",
        type: "object[]",
        description: "A list of agencies to display.",
        required: true,
        attributes: [
          { name: "name", type: "string" },
          { name: "address", type: "string" },
          { name: "phone", type: "string" },
          { name: "hours", type: "string" },
          { name: "website", type: "string" },
          { name: "notes", type: "string" },
          { name: "latitude", type: "number" },
          { name: "longitude", type: "number" },
        ],
      },
    ],
    render: ({ args }) => {
      const { category_name, agencies } = args;
      // Map incoming objects to Agency type
      const mappedAgencies: Agency[] = (agencies ?? []).map((a: any, idx: number) => ({
        id: a.id ?? `agency-${idx}`,
        name: a.name,
        address: a.address,
        latitude: a.latitude,
        longitude: a.longitude,
        category: category_name || "",
        contactInformation: [a.phone].filter(Boolean),
        hoursOfOperation: a.hours,
        website: a.website,
        description: a.notes,
      }));
      return <AgencyCarousel categoryName={category_name as string} agencies={mappedAgencies} />;
    },
  });

  useCopilotChatSuggestions({
    instructions: `Suggest actions like finding food banks, clothing closets, or shelters.`,
  });

  return (
    <AgenciesContext.Provider value={{
      categories: state.categories ?? [],
      selectedCategoryId: state.selected_agency_id,
    }}>
      {children}
    </AgenciesContext.Provider>
  );
};

export const useAgencies = () => {
  const context = useContext(AgenciesContext);
  if (context === undefined) {
    throw new Error("useAgencies must be used within an AgenciesProvider");
  }
  return context;
};