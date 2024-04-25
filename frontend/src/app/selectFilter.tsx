import * as React from "react"

import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectLabel,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"

// define the type for the props expected by the SelectIndustry component
interface SelectFilterProps {
  uniqueValues: string[]; // array of strings
  placeholder: string; 
  selectedValue: string;
  onValueChange: (value: string) => void;
}

export function SelectFilter({ uniqueValues, placeholder, selectedValue, onValueChange }: SelectFilterProps) {
  console.log("SelectFilter with selectedValue: ", selectedValue)
  
  return (
    <Select value={selectedValue} onValueChange={(value) => { onValueChange(value)}}>
      <SelectTrigger className="w-[200px]">
        <SelectValue placeholder={placeholder} />
      </SelectTrigger>
      <SelectContent>
        <SelectGroup>
          <SelectLabel>{placeholder}</SelectLabel>
          {uniqueValues.map((item: string) => (
            <SelectItem key={item} value={item}>
              {item}
            </SelectItem>
          ))}
        </SelectGroup>
      </SelectContent>
    </Select>
  )
}
