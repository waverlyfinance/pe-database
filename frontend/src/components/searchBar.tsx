import {
    Command,
    CommandEmpty,
    CommandGroup,
    CommandInput,
    CommandItem,
    CommandList,
  } from "@/components/ui/command"

  
  interface SearchBarProps {
    searchQuery: string;
    onSearchChange: (value: string) => void;
  }

export function SearchBar({ searchQuery, onSearchChange }: SearchBarProps) {
    // const [searchQuery, setSearchQuery] = useState("");

    return (
    <Command>
    <CommandInput placeholder="Semantically search for companies..." value={searchQuery} onValueChange={(value) => {
        onSearchChange(value)
        console.log("Search query: ", value)
        }}/>
    <CommandList>
        {/* <CommandEmpty>No results found.</CommandEmpty> */}
        <CommandGroup heading="Suggestions: 'DevOps', 'Cybersecurity', 'Supply chain', etc.">
        {/* <CommandItem>DevOps</CommandItem>
        <CommandItem>Cybersecurity</CommandItem>
        <CommandItem>Outpatient facilities</CommandItem>
        <CommandItem>Supply chain</CommandItem> */}
        </CommandGroup>
    </CommandList>
    </Command>
)};