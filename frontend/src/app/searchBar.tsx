// import {
//     Command,
//     CommandEmpty,
//     CommandGroup,
//     CommandInput,
//     CommandItem,
//     CommandList,
//   } from "@/components/ui/command"

import { Input } from "@/components/ui/input"

  interface SearchBarProps {
    searchQuery: string;
    onSearchChange: (value: string) => void;
  }

export function SearchBar({ searchQuery, onSearchChange }: SearchBarProps) {
    // const [searchQuery, setSearchQuery] = useState("");

    return (

    <Input placeholder="Semantically search for companies..." value={searchQuery} onChange={(e) => {
        onSearchChange(e.target.value)
        console.log("Search query: ", e)
        }}/>
)};