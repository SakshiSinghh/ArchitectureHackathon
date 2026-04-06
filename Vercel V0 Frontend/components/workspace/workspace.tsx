"use client"

import { LeftSidebar } from "./left-sidebar"
import { CenterPanel } from "./center-panel"
import { RightPanel } from "./right-panel"

export function Workspace() {
  return (
    <div className="flex h-screen overflow-hidden bg-background">
      <LeftSidebar />
      <div className="flex flex-1 overflow-hidden">
        <div className="flex-1 overflow-hidden">
          <CenterPanel />
        </div>
        <RightPanel />
      </div>
    </div>
  )
}
