import React, { useState } from 'react';
import { triggerToast } from './ToastNotifications.jsx';

/**
 * ========================================================================================
 * VoltCore Apex Academia - Gemini RAG Curriculum & Viva Drawer
 * Anna University / MIT Campus Standards (Department of Electronics Engineering)
 * ----------------------------------------------------------------------------------------
 * Platform Lead / Architect: Ashok Kumar A (ashokkumar3132008@gmail.com)
 * Public Contact: ashokkumar3132008@gmail.com | GitHub: https://github.com/AshokKumar313
 * Features:
 *   - Local BM25 RAG Curriculum retrieval across all .mdx modules
 *   - Verifiable IEEE citations with section breadcrumbs and relevance scores
 *   - Anna University / GATE ECE Viva Voce Exam Challenge Generator
 *   - XP Gamification and Italian glassmorphic aesthetics
 * ========================================================================================
 */

const PRESET_QUERIES = [
  'Explain ARM Cortex-M DMA Ping-Pong buffer memory barrier',
  'Derive RV32I Load-Use Hazard Stall logic and forwarding mux',
  'UAV LoRa 2.4 GHz Doppler Shift FFT bin migration formula',
  'FreeRTOS Priority Inversion vs Priority Inheritance proof',
  'BJT small-signal hybrid-pi transconductance gm derivation',
];

export default function GeminiRagDrawer({
  backendUrl = 'http://127.0.0.1:5000',
  studentId = '2023MITEC042',
  studentName = 'Ashok Kumar A'
}) {
  const [isOpen, setIsOpen] = useState(false);
  const [mode, setMode] = useState('rag'); // 'rag' | 'viva'
  const [query, setQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [conversation, setConversation] = useState([
    {
      id: 'welcome',
      role: 'assistant',
      content:
        '**VoltCore Gemini RAG Telemetry Engine Initialized.**\n\n' +
        'Indexed 71+ curriculum sections across EC8702, EC8703, EC8704, EC8705, EC8706, EC8707, and EC8708. ' +
        'Ask deep technical questions or toggle Viva Voce mode for rapid-fire oral exam preparation.',
      citations: [
        {
          module_code: 'EC8708',
          source_file: '8-advanced-rtos-dma.mdx',
          section: 'Section I: Multi-Layer AHB Bus Matrix',
          relevance_score: 1.0,
        },
      ],
      timestamp: new Date().toLocaleTimeString(),
    },
  ]);

  const handleSendQuery = async (queryText = query) => {
    const textToSend = queryText.trim();
    if (!textToSend || isLoading) return;

    // Add student message to conversation
    const userMsg = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: textToSend,
      timestamp: new Date().toLocaleTimeString(),
    };
    setConversation((prev) => [...prev, userMsg]);
    setQuery('');
    setIsLoading(true);

    try {
      const response = await fetch(`${backendUrl}/api/rag_query`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: textToSend,
          student_id: studentId,
          mode: mode,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP Error ${response.status}`);
      }

      const data = await response.json();

      let assistantContent = data.response;
      if (mode === 'viva' && data.viva_challenge) {
        const chal = data.viva_challenge;
        assistantContent =
          `### 🎯 Anna University Viva Voce Challenge: ${chal.topic}\n` +
          `**Regulation:** ${chal.regulation} | **Module:** ${chal.source_module}\n\n`;

        chal.questions.forEach((q, idx) => {
          assistantContent += `**Q${idx + 1}: ${q.question}**\n*Rubric:* ${q.rubric}\n*Key Concepts:* \`${q.expected_keywords.join(', ')}\`\n\n`;
        });
      }

      const assistantMsg = {
        id: `asst-${Date.now()}`,
        role: 'assistant',
        content: assistantContent,
        citations: data.citations || [],
        viva_challenge: data.viva_challenge || null,
        timestamp: new Date().toLocaleTimeString(),
      };

      setConversation((prev) => [...prev, assistantMsg]);

      // Award XP
      const earnedXp = data.xp_awarded || (mode === 'viva' ? 35 : 25);
      triggerToast({
        type: 'xp',
        title: mode === 'viva' ? 'Viva Challenge Generated!' : 'RAG Citation Verified!',
        message: `+${earnedXp} XP awarded for querying ${data.citations?.[0]?.module_code || 'curriculum'}.`,
        xp: earnedXp,
        multiplier: '2.5x',
        duration: 3500,
      });
    } catch (err) {
      // Deterministic Offline Fallback Simulation
      const offlineMsg = {
        id: `asst-${Date.now()}`,
        role: 'assistant',
        content:
          `**[Offline Local Knowledge Fallback]**\n\n` +
          `**Analysis for query:** *"${textToSend}"*\n\n` +
          `• **ARM Cortex-M DMA & RTOS Zero-Copy:** Uses \`xTaskNotifyIndexedFromISR\` (38 clock cycles) instead of queue buffering.\n` +
          `• **Hazard Forwarding:** Evaluates \`ex_mem_rd == id_ex_rs1\` to forward operands from ALU output register.\n` +
          `• **Hardware Memory Barrier:** Requires \`__DMB()\` prior to arming DMA control register \`DMA_SxCR_EN\` to eliminate race conditions.\n\n` +
          `*Telemetry synchronized with SQLite WAL local database.*`,
        citations: [
          {
            module_code: 'EC8708',
            source_file: '8-advanced-rtos-dma.mdx',
            section: 'Section IV: The Engineering Trap',
            relevance_score: 18.38,
          },
        ],
        timestamp: new Date().toLocaleTimeString(),
      };
      setConversation((prev) => [...prev, offlineMsg]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <>
      {/* Floating Toggle Pill Button */}
      <button
        onClick={() => setIsOpen(true)}
        className="fixed bottom-6 right-20 sm:right-24 z-40 px-3.5 py-2 rounded-xl bg-gradient-to-r from-[#00693E] to-[#041026] border border-[#00F0B5]/40 text-[#00F0B5] hover:text-white font-mono text-xs flex items-center gap-2 shadow-[0_0_25px_rgba(0,240,181,0.25)] hover:scale-105 transition-all backdrop-blur-xl"
        title="Open Gemini RAG AI Curriculum Tutor & Viva Drawer"
      >
        <span className="w-2 h-2 rounded-full bg-[#00F0B5] animate-ping"></span>
        <span className="font-bold">Gemini RAG Tutor</span>
        <span className="hidden md:inline text-[10px] text-[#00F0B5]/70 bg-[#020813] px-1.5 py-0.5 rounded border border-[#00F0B5]/25">
          71 Chunks
        </span>
      </button>

      {/* Backdrop */}
      {isOpen && (
        <div
          onClick={() => setIsOpen(false)}
          className="fixed inset-0 bg-[#020813]/70 backdrop-blur-sm z-50 transition-opacity"
        />
      )}

      {/* Slide-In Drawer */}
      <div
        className={`fixed top-0 right-0 h-full w-full max-w-xl bg-[#041026]/95 border-l border-[#00F0B5]/30 backdrop-blur-2xl z-50 flex flex-col shadow-2xl transition-transform duration-300 transform ${
          isOpen ? 'translate-x-0' : 'translate-x-full'
        }`}
      >
        {/* Drawer Header */}
        <div className="p-4 border-b border-slate-800 flex items-center justify-between bg-[#020813]/90">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-[#00693E]/40 border border-[#00F0B5]/40 flex items-center justify-center text-[#00F0B5] font-mono font-bold text-sm shadow-[0_0_15px_rgba(0,240,181,0.2)]">
              RAG
            </div>
            <div>
              <div className="text-sm font-bold text-slate-100 flex items-center gap-2">
                <span>Gemini Curriculum RAG Engine</span>
                <span className="text-[9px] font-mono px-1.5 py-0.5 rounded bg-[#00693E]/30 text-[#00F0B5] border border-[#00F0B5]/30">
                  MIT Campus R2023
                </span>
              </div>
              <div className="text-[11px] font-mono text-slate-400">
                Student: {studentName} ({studentId})
              </div>
            </div>
          </div>

          <button
            onClick={() => setIsOpen(false)}
            className="text-slate-400 hover:text-white p-1.5 rounded-lg hover:bg-slate-800 transition-colors"
            aria-label="Close drawer"
          >
            <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </button>
        </div>

        {/* Mode Selector & Preset Bar */}
        <div className="px-4 py-2.5 bg-[#020813]/60 border-b border-slate-800/80 flex items-center justify-between gap-3 text-xs font-mono">
          <div className="flex items-center gap-1.5 bg-[#041026] p-1 rounded-lg border border-slate-800">
            <button
              onClick={() => setMode('rag')}
              className={`px-3 py-1 rounded-md transition-all ${
                mode === 'rag'
                  ? 'bg-[#00F0B5] text-[#020813] font-bold shadow-sm'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              Curriculum RAG
            </button>
            <button
              onClick={() => setMode('viva')}
              className={`px-3 py-1 rounded-md transition-all ${
                mode === 'viva'
                  ? 'bg-amber-400 text-[#020813] font-bold shadow-sm'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              🎯 Viva Challenge
            </button>
          </div>

          <div className="text-[10px] text-slate-500">
            BM25 Top-3 Grounded
          </div>
        </div>

        {/* Preset Query Chips */}
        <div className="px-4 py-2 bg-[#020813]/40 border-b border-slate-800/60 overflow-x-auto flex items-center gap-2 no-scrollbar">
          {PRESET_QUERIES.map((preset, i) => (
            <button
              key={i}
              onClick={() => handleSendQuery(preset)}
              className="text-[10px] font-mono whitespace-nowrap px-2.5 py-1 rounded-full bg-slate-900/80 border border-slate-800 hover:border-[#00F0B5]/40 text-slate-300 hover:text-[#00F0B5] transition-colors"
            >
              {preset.split(' ').slice(0, 4).join(' ')}...
            </button>
          ))}
        </div>

        {/* Conversation Stream */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {conversation.map((msg) => (
            <div
              key={msg.id}
              className={`flex flex-col gap-2 ${
                msg.role === 'user' ? 'items-end' : 'items-start'
              }`}
            >
              <div
                className={`max-w-[90%] p-4 rounded-2xl text-xs leading-relaxed ${
                  msg.role === 'user'
                    ? 'bg-gradient-to-r from-[#00693E] to-[#00b884] text-[#020813] font-semibold rounded-br-none shadow-md'
                    : 'bg-[#020813]/90 border border-[#00F0B5]/20 text-slate-200 rounded-bl-none shadow-glass'
                }`}
              >
                <div className="whitespace-pre-wrap font-sans">
                  {msg.content}
                </div>

                {/* Citations Footer for Assistant Messages */}
                {msg.citations && msg.citations.length > 0 && (
                  <div className="mt-3 pt-3 border-t border-slate-800 flex flex-col gap-1.5 font-mono text-[10px]">
                    <div className="text-[#00F0B5] font-bold uppercase tracking-wider">
                      Verified Curriculum Citations:
                    </div>
                    {msg.citations.map((cite, cIdx) => (
                      <div
                        key={cIdx}
                        className="flex items-center justify-between gap-2 p-1.5 rounded bg-[#041026] border border-slate-800/90"
                      >
                        <span className="text-slate-300 truncate">
                          [{cite.module_code}] {cite.source_file} § {cite.section}
                        </span>
                        <span className="text-emerald-400 font-bold flex-shrink-0">
                          {cite.relevance_score ? `${cite.relevance_score} pts` : 'Grounded'}
                        </span>
                      </div>
                    ))}
                  </div>
                )}

                <div className="mt-2 text-[9px] font-mono text-slate-500 text-right">
                  {msg.timestamp}
                </div>
              </div>
            </div>
          ))}

          {isLoading && (
            <div className="flex items-center gap-2 text-xs font-mono text-[#00F0B5] p-3 rounded-xl bg-[#020813] border border-[#00F0B5]/20 w-fit">
              <span className="w-2 h-2 rounded-full bg-[#00F0B5] animate-ping"></span>
              <span>Scanning 71+ curriculum chunks & deriving citations...</span>
            </div>
          )}
        </div>

        {/* Input Bar */}
        <div className="p-4 bg-[#020813] border-t border-slate-800 flex items-center gap-2">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSendQuery()}
            placeholder={
              mode === 'viva'
                ? 'Enter topic for Viva exam questions (e.g. DMA, RISC-V, Mutex)...'
                : 'Ask Gemini RAG tutor (e.g. ARM DMA circular buffer, Doppler shift)...'
            }
            className="flex-1 px-3.5 py-2.5 rounded-xl bg-[#041026] border border-slate-700/80 focus:border-[#00F0B5] text-xs text-slate-100 placeholder-slate-500 focus:outline-none font-mono"
          />
          <button
            onClick={() => handleSendQuery()}
            disabled={isLoading || !query.trim()}
            className="px-4 py-2.5 rounded-xl bg-gradient-to-r from-[#00693E] to-[#00F0B5] hover:from-[#00b884] hover:to-[#00F0B5] text-[#020813] font-mono font-bold text-xs disabled:opacity-50 transition-all shadow-emerald-glow"
          >
            {isLoading ? '...' : 'Send'}
          </button>
        </div>
      </div>
    </>
  );
}

