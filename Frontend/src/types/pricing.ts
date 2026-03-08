export interface RoomPricing {
  id: number;
  room_type: string;
  capacity: string;
  price_per_night: number;
  is_active: boolean;
  created_at: string;
  updated_at?: string;
}

export interface RoomPricingCreate {
  room_type: string;
  capacity: string;
  price_per_night: number;
  is_active?: boolean;
}

export interface RoomPricingUpdate {
  room_type?: string;
  capacity?: string;
  price_per_night?: number;
  is_active?: boolean;
}

export interface PricingMatrix {
  room_type: string;
  prices: {
    [capacity: string]: number | null;
  };
}

export interface PricingOptions {
  room_types: string[];
  capacities: string[];
}

