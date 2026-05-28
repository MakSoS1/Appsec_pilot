import { X } from "lucide-react";
import { Button, Card } from "@/components/ui-kit";
import { ScanTemplate, scanTemplates } from "@/lib/scan-templates";

type ScanTemplateDialogProps = {
  open: boolean;
  title: string;
  onClose: () => void;
  onSelect: (template: ScanTemplate) => void;
};

export function ScanTemplateDialog({ open, title, onClose, onSelect }: ScanTemplateDialogProps) {
  if (!open) return null;
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/45 p-4">
      <Card className="w-full max-w-2xl">
        <div className="mb-4 flex items-start justify-between gap-3">
          <div>
            <h2 className="text-lg font-semibold">{title}</h2>
            <p className="text-sm text-muted-foreground">
              Выберите шаблон запуска. Профиль можно изменить в следующем скане.
            </p>
          </div>
          <Button variant="ghost" size="sm" onClick={onClose}>
            <X className="h-4 w-4" />
          </Button>
        </div>
        <div className="space-y-2">
          {scanTemplates.map((template) => (
            <button
              key={template.id}
              type="button"
              onClick={() => onSelect(template)}
              className="w-full rounded-md border border-border p-3 text-left transition-colors hover:bg-muted/40"
            >
              <div className="flex items-center justify-between gap-3">
                <div className="text-sm font-semibold">{template.title}</div>
                <span className="rounded bg-muted px-2 py-0.5 text-xs">{template.profile}</span>
              </div>
              <p className="mt-1 text-sm text-muted-foreground">{template.description}</p>
            </button>
          ))}
        </div>
        <div className="mt-4 flex justify-end">
          <Button variant="outline" onClick={onClose}>
            Отмена
          </Button>
        </div>
      </Card>
    </div>
  );
}
