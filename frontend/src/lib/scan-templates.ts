export type ScanTemplate = {
  id: "passive" | "safe-active" | "full-lab";
  title: string;
  description: string;
  profile: "passive" | "safe-active" | "full-lab";
};

export const scanTemplates: ScanTemplate[] = [
  {
    id: "passive",
    title: "Пассивный",
    description: "Только безопасный анализ без активных модифицирующих запросов.",
    profile: "passive",
  },
  {
    id: "safe-active",
    title: "Safe Active",
    description: "Рекомендуемый режим: безопасные активные проверки в рамках scope.",
    profile: "safe-active",
  },
  {
    id: "full-lab",
    title: "Full Lab",
    description: "Расширенный лабораторный режим для тренировочных стендов.",
    profile: "full-lab",
  },
];
