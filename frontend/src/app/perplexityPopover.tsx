import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { PerplexityDataType } from "./custom-search"
import { Item } from "@radix-ui/react-select"


interface PerplexityPopoverProps {
  data: PerplexityDataType[];
  showPopover: boolean;
  onPopoverTrigger: (show: boolean) => void;
}

export function PerplexityPopover({ data, showPopover, onPopoverTrigger }: PerplexityPopoverProps) {

  // if popoverTrigger is false, then don't display anything
  if (!showPopover) {
    return null;
  }

  const handleClose = () => {
    onPopoverTrigger(false);
  };

  return (
    <Dialog open>
      <DialogContent className="sm:max-w-full max-h-[80vh] overflow-auto">
        <DialogHeader>
          <DialogTitle>Search results</DialogTitle>
          <DialogDescription>
            For each selected company, here are the results of your query:  
          </DialogDescription>
        </DialogHeader>
        <div className="grid gap-4 py-4">
          {data.map((item, index) => (
            <div key={index}>
              <Card>
                <CardHeader>
                  <CardTitle>{item.company_name}</CardTitle>
                  <CardDescription>{item.firm}</CardDescription>
                </CardHeader>
                <CardContent>
                  <p>{item.perplexityOutput}</p>
                </CardContent>
              </Card>

              {/* <Label htmlFor="company_name" className="text-right">
                {item.company_name}
              </Label> */}
            </div>
          ))}
        </div>

        <DialogFooter>
          <Button type="submit" onClick={handleClose}>Close</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
