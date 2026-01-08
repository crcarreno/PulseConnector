import { Button } from "@/components/Button"
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/Dialog"
import { Input } from "@/components/Input"
import { Label } from "@/components/Label"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/Select"
import { dialects } from "@/data/data"

export type ModalAddConnectionProps = {
  children: React.ReactNode
}

export function ModalAddConnection({ children }: ModalAddConnectionProps) {
  return (
    <Dialog>
      <DialogTrigger asChild>{children}</DialogTrigger>
      <DialogContent className="sm:max-w-lg">
        <form>
          <DialogHeader>
            <DialogTitle>Add different database engine connections</DialogTitle>
            <DialogDescription className="mt-1 text-sm leading-6">
              Add database connections
            </DialogDescription>

            <div className="mt-4">
              <Label htmlFor="dialect-new-connection" className="font-medium">
                Select database
              </Label>
              <Select>
                <SelectTrigger
                  id="dialect-new-connection"
                  name="dialect-new-connection"
                  className="mt-2"
                >
                  <SelectValue placeholder="Select database..." />
                </SelectTrigger>
                <SelectContent align="end">
                  {dialects.map((dialect) => (
                    <SelectItem
                      key={dialect.value}
                      value={dialect.value}
                      disabled={dialect.value === "admin"}
                    >
                      {dialect.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="mt-4">
              <Label htmlFor="ip-connection" className="font-medium">
                IP Address
              </Label>
              <Input
                id="ip-connection"
                name="ip-connection"
                placeholder="0.0.0.0"
                className="mt-2"
              />
            </div>

            <div className="mt-4">
              <Label htmlFor="port-connection" className="font-medium">
                Port
              </Label>
              <Input
                id="port-connection"
                name="port-connection"
                placeholder="5443"
                className="mt-2"
              />
            </div>

            <div className="mt-4">
              <Label htmlFor="user-connection" className="font-medium">
                User
              </Label>
              <Input
                id="user-connection"
                name="user-connection"
                placeholder="User connection.."
                className="mt-2"
              />
            </div>

            <div className="mt-4">
              <Label htmlFor="pass-connection" className="font-medium">
                Password
              </Label>
              <Input
                id="pass-connection"
                name="pass-connection"
                placeholder="Pass connection.."
                className="mt-2"
              />
            </div>

            <div className="mt-4">
              <Label htmlFor="database-connection" className="font-medium">
                Database
              </Label>
              <Input
                id="database-connection"
                name="database-connection"
                placeholder="Database connection.."
                className="mt-2"
              />
            </div>
          </DialogHeader>
          <DialogFooter className="mt-6">

            <DialogClose asChild>
              <Button
                className="mt-2 w-full sm:mt-0 sm:w-fit"
                variant="secondary"
              >
                Go back
              </Button>
            </DialogClose>

            <DialogClose asChild>
              <Button
                className="mt-2 w-full sm:mt-0 sm:w-fit"
                variant="warning"
              >
                Test Connection
              </Button>
            </DialogClose>

            <DialogClose asChild>
              <Button type="submit" className="w-full sm:w-fit">
                Add user
              </Button>
            </DialogClose>

          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}
