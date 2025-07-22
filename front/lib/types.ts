export type Agency = {
  id: string;
  name: string;
  address: string;
  latitude: number;
  longitude: number;
  category: string; // e.g., "Food Bank", "Shelter", "Mental Health Support"
  contactInformation: string[];
  hoursOfOperation?: string; 
  website?: string;
  description?: string;
};
  
export type AgencyCategory = {
  id: string;
  name: string;
  center_latitude: number;
  center_longitude: number;
  zoom_level: number | 13; // Default zoom level
  agencies: Agency[];
};

export type SearchProgress = {
  query: string;
  done: boolean;
};

export type AgentState = {
  agencies: Agency[];
  selected_agency_id: string | null;
  search_progress?: SearchProgress[];
};


// You can have default or empty initial data
export const defaultCategories: AgencyCategory[] = [];