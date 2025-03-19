import React, { useEffect, useRef, useState } from "react";
import cn from "classnames";
import { RiSidebarFoldLine, RiSidebarUnfoldLine } from "react-icons/ri";
import Select from "react-select";
import { useLiveAPIContext } from "../../contexts/LiveAPIContext";
import { useLoggerStore } from "../../utils/store-logger";
import Logger, { LoggerFilterType } from "../logger/Logger";
import "./side-panel.scss";

const filterOptions = [
  { value: "conversations", label: "Conversations" },
  { value: "tools", label: "Tool Use" },
  { value: "none", label: "All" },
];

export default function SidePanel() {
  const { connected, client } = useLiveAPIContext();
  const [open, setOpen] = useState(true);
  const [showDisclaimer, setShowDisclaimer] = useState(true); // State for disclaimer modal
  const loggerRef = useRef<HTMLDivElement>(null);
  const loggerLastHeightRef = useRef<number>(-1);
  const { log, logs } = useLoggerStore();
  const [textInput, setTextInput] = useState("");
  const [selectedOption, setSelectedOption] = useState<{ value: string; label: string } | null>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  // Scroll the log to the bottom when new logs come in
  useEffect(() => {
    if (loggerRef.current) {
      const el = loggerRef.current;
      const scrollHeight = el.scrollHeight;
      if (scrollHeight !== loggerLastHeightRef.current) {
        el.scrollTop = scrollHeight;
        loggerLastHeightRef.current = scrollHeight;
      }
    }
  }, [logs]);

  // Listen for log events and store them
  useEffect(() => {
    client.on("log", log);
    return () => {
      client.off("log", log);
    };
  }, [client, log]);

  const handleSubmit = () => {
    client.send([{ text: textInput }]);
    setTextInput("");
    if (inputRef.current) {
      inputRef.current.innerText = "";
    }
  };

  return (
    <div className={`side-panel ${open ? "open" : ""}`}>
      {/* Disclaimer Modal */}
      {showDisclaimer && (
        <div className="disclaimer-modal">
          <div className="disclaimer-content">
            <h2>Disclaimer</h2>
            <p>
    This AI Agent has been developed in collaboration with Agentic AI and leverages data from the Official Gazette, regulatory authorities’ official publications, and other reliable public sources. The AI Agent aims to assist users in tracking regulatory changes, analyzing documents, and accessing relevant information efficiently.
    This system is designed in alignment with Google’s Trustworthy AI and Explainable AI principles, ensuring transparency, reliability, and explainability in its decision-making processes. However:
    The information provided by the AI Agent is for informational purposes only and does not constitute legal, financial, or regulatory advice.
    Users are responsible for verifying the accuracy and timeliness of the information from official sources.
    While the AI Agent proactively notifies users of regulatory updates, the interpretation and application of such updates remain solely the user’s responsibility.
    The Fact Checker feature is designed to identify manipulative or misleading content; however, it does not guarantee the detection of all misinformation.
    Any decisions or actions taken based on the information provided by this AI Agent are entirely at the user's discretion and responsibility. Users should consider seeking professional advice for specific regulatory or legal matters.
 
            </p>
            <button className="disclaimer-btn" onClick={() => setShowDisclaimer(false)}>I Agree</button>
          </div>
        </div>
      )}

      <header className="top">
        <div className="logo-container">
          <img src="/regupng.png" alt="Regu SELIN" className="logo" />
        </div>
        <h2>Regu AI</h2>
        {open ? (
          <button className="opener" onClick={() => setOpen(false)}>
            <RiSidebarFoldLine color="#b4b8bb" />
          </button>
        ) : (
          <button className="opener" onClick={() => setOpen(true)}>
            <RiSidebarUnfoldLine color="#b4b8bb" />
          </button>
        )}
      </header>
      <section className="indicators">
        <Select
          className="react-select"
          classNamePrefix="react-select"
          styles={{
            control: (baseStyles) => ({
              ...baseStyles,
              background: "var(--Neutral-15)",
              color: "var(--Neutral-90)",
              minHeight: "33px",
              maxHeight: "33px",
              border: 0,
            }),
            option: (styles, { isFocused, isSelected }) => ({
              ...styles,
              backgroundColor: isFocused ? "var(--Neutral-30)" : isSelected ? "var(--Neutral-20)" : undefined,
            }),
          }}
          defaultValue={selectedOption}
          options={filterOptions}
          onChange={(e) => {
            setSelectedOption(e);
          }}
        />
        <div className={cn("streaming-indicator", { connected })}>
          {connected ? `🔵${open ? " Streaming" : ""}` : `⏸️${open ? " Paused" : ""}`}
        </div>
      </section>
      <div className="side-panel-container" ref={loggerRef}>
        <Logger filter={(selectedOption?.value as LoggerFilterType) || "none"} />
      </div>
      <div className={cn("input-container", { disabled: !connected })}>
        <div className="input-content">
          <textarea
            className="input-area"
            ref={inputRef}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                e.stopPropagation();
                handleSubmit();
              }
            }}
            onChange={(e) => setTextInput(e.target.value)}
            value={textInput}
          ></textarea>
          <span className={cn("input-content-placeholder", { hidden: textInput.length })}>Type&nbsp;something...</span>
          <button className="send-button material-symbols-outlined filled" onClick={handleSubmit}>send</button>
        </div>
      </div>
    </div>
  );
}
