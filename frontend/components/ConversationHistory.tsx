"use client";

import { useEffect, useState } from "react";
import type { ChatMessage } from "../types";
import { Download, Trash2, X, Bookmark, FileJson } from "lucide-react";

export interface SavedSession {
  id: string;
  characterId: string;
  characterName: string;
  timestamp: number;
  messages: ChatMessage[];
}

interface ConversationHistoryProps {
  isOpen: boolean;
  onClose: () => void;
  currentMessages: ChatMessage[];
  characterId: string;
  characterName: string;
  onLoadSession: (session: SavedSession) => void;
}

export function ConversationHistory({
  isOpen,
  onClose,
  currentMessages,
  characterId,
  characterName,
  onLoadSession,
}: ConversationHistoryProps) {
  const [sessions, setSessions] = useState<SavedSession[]>([]);

  // Load sessions from localStorage
  useEffect(() => {
    const saved = localStorage.getItem("history_simulation_sessions");
    if (saved) {
      try {
        setSessions(JSON.parse(saved));
      } catch (e) {
        console.error(e);
      }
    }
  }, [isOpen]);

  const saveCurrentSession = () => {
    if (currentMessages.length === 0) return;

    const newSession: SavedSession = {
      id: `${Date.now()}`,
      characterId,
      characterName,
      timestamp: Date.now(),
      messages: currentMessages,
    };

    const updated = [newSession, ...sessions.filter((s) => s.messages.length > 0)];
    localStorage.setItem("history_simulation_sessions", JSON.stringify(updated));
    setSessions(updated);
    alert("Đã lưu hội thoại thành công!");
  };

  const deleteSession = (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!confirm("Bạn có chắc chắn muốn xóa hội thoại này?")) return;
    const updated = sessions.filter((s) => s.id !== id);
    localStorage.setItem("history_simulation_sessions", JSON.stringify(updated));
    setSessions(updated);
  };

  const exportSession = (session: SavedSession, e: React.MouseEvent) => {
    e.stopPropagation();
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(session, null, 2));
    const downloadAnchor = document.createElement("a");
    downloadAnchor.setAttribute("href", dataStr);
    downloadAnchor.setAttribute("download", `Hoi_thoai_${session.characterName.replace(/\s+/g, "_")}_${new Date(session.timestamp).toLocaleDateString()}.json`);
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
  };

  return (
    <div className={`history-panel ${isOpen ? "open" : ""}`}>
      <div className="history-panel-header">
        <h3 className="history-panel-title">Lịch Sử Hội Thoại</h3>
        <button onClick={onClose} className="text-muted hover:text-[#e5bd3b]" aria-label="Đóng lịch sử">
          <X size={20} />
        </button>
      </div>

      <div className="p-4 border-b border-[rgba(229,189,59,0.15)] flex justify-between gap-3">
        <button
          onClick={saveCurrentSession}
          disabled={currentMessages.length === 0}
          className="flex-1 flex items-center justify-center gap-2 rounded-md bg-[#e5bd3b] text-[#1c150d] py-2 px-3 text-sm font-semibold disabled:opacity-40 disabled:cursor-not-allowed hover:bg-[#f0cc58] transition"
        >
          <Bookmark size={16} />
          Lưu hội thoại hiện tại
        </button>
      </div>

      <div className="history-panel-body">
        {sessions.length === 0 ? (
          <div className="history-empty">Chưa có hội thoại nào được lưu.</div>
        ) : (
          sessions.map((session) => (
            <div
              key={session.id}
              onClick={() => onLoadSession(session)}
              className="history-session-card"
            >
              <div className="flex justify-between items-start">
                <div>
                  <h4 className="history-session-title">{session.characterName}</h4>
                  <p className="history-session-meta">
                    {new Date(session.timestamp).toLocaleString("vi-VN", {
                      dateStyle: "short",
                      timeStyle: "short",
                    })}
                  </p>
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={(e) => exportSession(session, e)}
                    className="text-muted hover:text-[#e5bd3b] p-1"
                    title="Xuất file JSON"
                  >
                    <Download size={14} />
                  </button>
                  <button
                    onClick={(e) => deleteSession(session.id, e)}
                    className="text-muted hover:text-[#ff4d4d] p-1"
                    title="Xóa"
                  >
                    <Trash2 size={14} />
                  </button>
                </div>
              </div>
              <p className="history-session-preview">
                {session.messages[0]?.role === "user" ? "Hỏi: " : "Đáp: "}
                {session.messages[0]?.content || "..."}
              </p>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
