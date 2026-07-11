"use client";

import { useState } from "react";
import {
  Button,
  Chip,
  NavigationControl,
  Panel,
  Segmented,
  ThemeDial,
} from "@/components";

/**
 * ControlsLab — client wrapper for the Controls section's static demos.
 * Required because Segmented is a client component and accepts an onChange
 * function. The server-rendered /system page passes JSX children that
 * include Segmented instances, so they must originate from a client tree.
 */
export function ControlsLab() {
  const [t1, setT1] = useState<"24h" | "7d" | "30d">("24h");
  const [m1, setM1] = useState<"ops" | "dev" | "res">("ops");
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      <Panel title="Buttons" headerRight={<Chip>3 variants</Chip>}>
        <div className="ort-content-module flex flex-wrap items-center gap-3">
          <Button variant="primary">Primary</Button>
          <Button variant="default">Default</Button>
          <Button variant="ghost">Ghost</Button>
          <Button variant="default" size="sm">
            Small
          </Button>
          <Button variant="default" disabled>
            Disabled
          </Button>
        </div>
      </Panel>
      <Panel title="Segmented Control" headerRight={<Chip>keyboard</Chip>}>
        <div className="ort-content-module flex flex-wrap items-center gap-4">
          <Segmented
            ariaLabel="Time range"
            value={t1}
            onChange={setT1}
            options={[
              { value: "24h", label: "24H" },
              { value: "7d", label: "7D" },
              { value: "30d", label: "30D" },
            ]}
          />
          <Segmented
            ariaLabel="Mode"
            value={m1}
            onChange={setM1}
            options={[
              { value: "ops", label: "OPS" },
              { value: "dev", label: "DEV" },
              { value: "res", label: "RES" },
            ]}
          />
        </div>
      </Panel>
      <Panel title="ThemeDial" headerRight={<Chip tone="signal">accent</Chip>}>
        <div className="ort-content-module">
          <ThemeDial />
        </div>
      </Panel>
      <Panel title="Navigation Control" headerRight={<Chip>aria-current</Chip>}>
        <div className="ort-content-module">
          <NavigationControl
            currentId="tools"
            items={[
              { id: "home", label: "Home" },
              { id: "tools", label: "Tools" },
              { id: "kits", label: "Prompt Kits" },
              { id: "learn", label: "Learn" },
              { id: "jobs", label: "Jobs" },
            ]}
          />
        </div>
      </Panel>
    </div>
  );
}