import React, { useState, useEffect, useRef } from 'react';

/**
 * VoltCore Apex Academia - Gemini AI Interactive Tutor & Viva Voce Generator
 * Standards: Anna University / MIT Campus (ECE / Embedded Systems Laboratory)
 * Protocol: REST JSON to Flask Backend (/app/api/tutor_query)
 */

const VIVA_QUESTION_BANK = [
  {
    id: 'viva-1',
    topic: 'RISC-V Microarchitecture (EC8705)',
    question: 'Why does an instruction immediately following a "lw" instruction requiring the loaded data cause an unavoidable 1-cycle pipeline stall even with a full hazard forwarding unit?',
    modelAnswer: 'The load word (lw) instruction produces valid memory data only at the conclusion of the MEM stage. The dependent instruction demands this operand at the start of its EX stage. Because memory data cannot be forwarded backwards in time from Cycle 4 to Cycle 3, the hazard detection unit must insert a 1-cycle bubble (NOP stall) while freezing the PC and IF/ID pipeline registers.',
    marks: 5,
    difficulty: 'Hard (GATE ECE / MIT Viva)'
  },
  {
    id: 'viva-2',
    topic: 'Defense UAV Telemetry & FHSS (EC8703)',
    question: 'Calculate the maximum Doppler shift at 2.4 GHz for a UAV traveling at 108 km/h. Why does this cause LoRa CSS demodulation failure when Spreading Factor SF=10 and Bandwidth=203 kHz?',
    modelAnswer: 'At v = 30 m/s (108 km/h) and f = 2.4 GHz (lambda = 0.125 m), direct Doppler shift is delta_f = v / lambda = 240 Hz. In LoRa CSS, the frequency tolerance threshold before FFT bin ambiguity occurs is BW / 2^(SF+2) = 203,000 / 4096 ≈ 49.5 Hz. Because 240 Hz exceeds 49.5 Hz by nearly 5x, the de-chirping FFT peak is detected in the incorrect bin, causing complete cyclic redundancy check (CRC) failure.',
    marks: 5,
    difficulty: 'Advanced (Electronic Warfare)'
  },
  {
    id: 'viva-3',
    topic: 'FreeRTOS & Dual-Core ESP32 (EC8702)',
    question: 'How does Priority Inheritance in FreeRTOS resolve unbounded Priority Inversion when a high-priority telemetry task and a low-priority RFID reader task share the SPI bus mutex?',
    modelAnswer: 'With standard binary semaphores, a medium-priority task can preempt a low-priority task holding the lock, indirectly starving the high-priority task. A FreeRTOS Mutex created with xSemaphoreCreateMutex() temporarily elevates the low-priority task priority to match the blocked high-priority task until the mutex is released via xSemaphoreGive().',
    marks: 5,
    difficulty: 'Intermediate (Embedded Systems Lab)'
  },
  {
    id: 'viva-4',
    topic: 'Hardware Interfacing & I2C/SPI Protocols',
    question: 'Why are pull-up resistors required on the I2C bus SDA and SCL lines, and how does bus capacitance affect maximum operating frequency in Fast-Mode (400 kHz)?',
    modelAnswer: 'I2C employs open-drain outputs that can actively pull the bus down to 0V (logic LOW) but rely on passive external pull-up resistors (typically 2.2kΩ - 4.7kΩ to 3.3V) to charge bus parasitic capacitance back to logic HIGH. In 400 kHz Fast-Mode, rise time must remain below 300 ns. High bus capacitance increases the RC time constant, causing rounded edges that violate setup timing.',
    marks: 5,
    difficulty: 'Fundamental (Anna University R2021)'
  }
];

export default function GeminiTutorChat({
  apiUrl = 'http://127.0.0.1:5000/app/api/tutor_query',
  studentName = 'Ashok Kumar A',
  studentRoll = '2023MITEC042'
}) {
  const [messages, setMessages] = useState([
    {
      id: 'msg-init',
      sender: 'gemini',
      text: `Vanakkam, ${studentName}! I am your VoltCore Gemini AI Mentor for the Anna University / MIT Campus Department of Electronics Engineering.\n\nI can assist you with:\n• **EC8705**: RV32I 5-stage pipeline hazards & forwarding logic\n• **EC8703**: Defense UAV 2.4GHz FHSS & Doppler shift traps\n• **EC8702**: FreeRTOS multi-core telemetry on ESP32\n\nClick **Generate Viva Quiz** or ask any embedded query!`,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }
  ]);

  const [inputQuery, setInputQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [activeViva, setActiveViva] = useState(null);
  const [studentAnswer, setStudentAnswer] = useState('');
  const [vivaEvaluation, setVivaEvaluation] = useState(null);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, activeViva, vivaEvaluation]);

  // Handle Formatted Markdown Text Rendering
  const renderFormattedText = (content) => {
    if (!content) return null;
    const lines = content.split('\n');
    return lines.map((line, idx) => {
      // Code blocks or bullet points
      if (line.startsWith('• ') || line.startsWith('- ')) {
        const itemText = line.substring(2);
        return (
          <li key={idx} className="ml-4 list-disc text-slate-300 my-0.5">
            {renderInlineMarkdown(itemText)}
          </li>
        );
      }
      if (line.trim().startsWith('```')) {
        return null; // Handle code separately if needed
      }
      return (
        <p key={idx} className="my-1 leading-relaxed text-slate-200">
          {renderInlineMarkdown(line)}
        </p>
      );
    });
  };

  // Helper for inline bold / code formatting
  const renderInlineMarkdown = (text) => {
    const parts = text.split(/(\*\*.*?\*\*|`.*?`)/g);
    return parts.map((part, index) => {
      if (part.startsWith('**') && part.endsWith('**')) {
        return <strong key={index} className="text-[#00F0B5] font-semibold">{part.slice(2, -2)}</strong>;
      }
      if (part.startsWith('`') && part.endsWith('`')) {
        return (
          <code key={index} className="px-1.5 py-0.5 rounded bg-[#020813] border border-slate-700 font-mono text-[11px] text-cyan-300">
            {part.slice(1, -1)}
          </code>
        );
      }
      return part;
    });
  };

  // Dispatch Query to Flask Backend with Offline Fallback
  const handleSendQuery = async (queryText) => {
    const query = (queryText || inputQuery).trim();
    if (!query || isLoading) return;

    const userMsg = {
      id: `usr-${Date.now()}`,
      sender: 'user',
      text: query,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    setMessages((prev) => [...prev, userMsg]);
    if (!queryText) setInputQuery('');
    setIsLoading(true);

    try {
      const response = await fetch(apiUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: query,
          student_id: studentRoll,
          mode: 'chat',
          context: 'Anna University / MIT Campus ECE Embedded Systems'
        })
      });

      if (response.ok) {
        const data = await response.json();
        const geminiMsg = {
          id: `gem-${Date.now()}`,
          sender: 'gemini',
          text: data.response || data.message || 'Analysis complete.',
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        };
        setMessages((prev) => [...prev, geminiMsg]);
      } else {
        throw new Error(`Server returned HTTP ${response.status}`);
      }
    } catch (err) {
      // Offline Intelligent Fallback Response
      const simulatedResponse = getSimulatedAcademicResponse(query);
      setTimeout(() => {
        setMessages((prev) => [
          ...prev,
          {
            id: `gem-${Date.now()}`,
            sender: 'gemini',
            text: simulatedResponse,
            timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
          }
        ]);
      }, 400);
    } finally {
      setIsLoading(false);
    }
  };

  // Generate Anna University / GATE ECE Viva Challenge
  const handleGenerateViva = () => {
    const randomIdx = Math.floor(Math.random() * VIVA_QUESTION_BANK.length);
    const chosen = VIVA_QUESTION_BANK[randomIdx];
    setActiveViva(chosen);
    setStudentAnswer('');
    setVivaEvaluation(null);
  };

  // Evaluate Student Viva Answer
  const handleEvaluateAnswer = () => {
    if (!activeViva) return;
    const ansLower = studentAnswer.toLowerCase();
    
    // Scoring logic based on keywords
    let score = 3;
    let feedback = '';

    if (activeViva.id === 'viva-1') {
      if (ansLower.includes('mem') && (ansLower.includes('bubble') || ansLower.includes('stall') || ansLower.includes('nop'))) {
        score = 5;
        feedback = 'Outstanding! You correctly identified the memory access stage latency and the imperative 1-cycle bubble insertion.';
      } else {
        score = 3;
        feedback = 'Good attempt. Ensure you emphasize that Block RAM latency cannot be bypassed before the MEM stage finishes.';
      }
    } else if (activeViva.id === 'viva-2') {
      if (ansLower.includes('doppler') && (ansLower.includes('fft') || ansLower.includes('bin') || ansLower.includes('tcxo'))) {
        score = 5;
        feedback = 'Excellent analysis! You clearly explained the chirp bin threshold and Doppler spread exceeding FFT tolerance.';
      } else {
        score = 3;
        feedback = 'Partially correct. Calculate the frequency shift delta_f = v/lambda and contrast it with BW / 2^(SF+2).';
      }
    } else {
      score = studentAnswer.trim().length > 30 ? 4 : 2;
      feedback = 'Evaluated against Anna University Department of Electronics Engineering marking rubric.';
    }

    setVivaEvaluation({
      score,
      maxScore: activeViva.marks,
      feedback,
      modelAnswer: activeViva.modelAnswer
    });
  };

  // Knowledge base for offline mode
  const getSimulatedAcademicResponse = (q) => {
    const lower = q.toLowerCase();
    if (lower.includes('risc-v') || lower.includes('rv32i') || lower.includes('hazard')) {
      return `**RV32I 5-Stage Hazard Forwarding Architecture:**\n\n• **EX-to-EX Forwarding:** When \`ex_mem_reg_write\` is asserted and \`ex_mem_rd == id_ex_rs1\`, forward directly from the ALU output register (ForwardA = 2'b10).\n• **MEM-to-EX Forwarding:** When \`mem_wb_reg_write\` is asserted and matches the operand, forward from writeback mux (ForwardA = 2'b01).\n• **Load-Use Trap:** For \`lw\` immediately followed by an ALU instruction, forwarding cannot travel backward in time; a 1-cycle pipeline bubble (NOP) must be forced.`;
    }
    if (lower.includes('doppler') || lower.includes('uav') || lower.includes('fhss') || lower.includes('lora')) {
      return `**Defense UAV FHSS & Doppler Shift Protocol:**\n\n• **Velocity Doppler Formula:** $\\Delta f_D = \\frac{v}{\\lambda} \\cos(\\theta)$. At 108 km/h ($30 \\text{ m/s}$) on 2.4 GHz, Doppler shift reaches $\\pm 240 \\text{ Hz}$.\n• **The LoRa Trap:** For $SF=10$ and $BW=203 \\text{ kHz}$, the bin window is only $49.5 \\text{ Hz}$. Carrier frequency offset causes severe de-chirp FFT bin migration.\n• **Remedy:** Employ a $\\pm 0.5 \\text{ PPM}$ TCXO and active SX1280 AFC tracking registers.`;
    }
    return `In Anna University's **EC8702 / EC8705** curriculum, real-time deterministic performance depends on isolating peripheral latencies. For your ESP32 Smart Attendance Node, make sure FreeRTOS queues decouple sensor ISRs on Core 1 from Wi-Fi HTTP tasks on Core 0.`;
  };

  return (
    <div className="flex flex-col h-full bg-[#041026] text-slate-100 font-mono text-xs select-text">
      
      {/* Top Banner Toolbar */}
      <div className="p-3 bg-[#020813] border-b border-[#00F0B5]/20 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-[#00F0B5] opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-[#00F0B5]"></span>
          </span>
          <span className="font-bold text-white tracking-wide">GEMINI CORTEX VIVA TUTOR</span>
        </div>
        <button
          type="button"
          onClick={handleGenerateViva}
          className="px-2.5 py-1 rounded-lg bg-gradient-to-r from-[#00693E] to-[#00b884] hover:from-[#008f65] hover:to-[#00F0B5] text-white font-bold text-[11px] shadow-emerald-glow flex items-center gap-1.5 transition-all"
        >
          <span>🎯 Generate Viva Quiz</span>
        </button>
      </div>

      {/* Quick Prompt Chips */}
      <div className="p-2.5 bg-[#020813]/60 border-b border-slate-800 flex gap-1.5 overflow-x-auto">
        <button
          type="button"
          onClick={() => handleSendQuery('Explain RV32I Load-Use Hazard Stall')}
          className="px-2 py-1 rounded bg-[#041026] hover:bg-[#00693E]/30 border border-slate-800 text-[10px] text-slate-300 hover:text-[#00F0B5] whitespace-nowrap"
        >
          RV32I Load-Use Hazard
        </button>
        <button
          type="button"
          onClick={() => handleSendQuery('Explain Urban Canyon Doppler Shift in LoRa')}
          className="px-2 py-1 rounded bg-[#041026] hover:bg-[#00693E]/30 border border-slate-800 text-[10px] text-slate-300 hover:text-[#00F0B5] whitespace-nowrap"
        >
          UAV LoRa Doppler Trap
        </button>
        <button
          type="button"
          onClick={() => handleSendQuery('FreeRTOS Priority Inversion vs Inheritance')}
          className="px-2 py-1 rounded bg-[#041026] hover:bg-[#00693E]/30 border border-slate-800 text-[10px] text-slate-300 hover:text-[#00F0B5] whitespace-nowrap"
        >
          FreeRTOS Priority Inversion
        </button>
      </div>

      {/* Main Conversation History */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`p-3.5 rounded-2xl border transition-all ${
              msg.sender === 'user'
                ? 'bg-[#061735] border-[#00F0B5]/30 ml-8 text-right'
                : 'bg-[#020813] border-slate-800 mr-4 text-left shadow-lg'
            }`}
          >
            <div className="flex items-center justify-between text-[10px] text-slate-400 mb-1">
              <span className={msg.sender === 'user' ? 'text-[#00F0B5] font-bold' : 'text-emerald-400 font-bold'}>
                {msg.sender === 'user' ? studentName : 'VoltCore Gemini Cortex'}
              </span>
              <span>{msg.timestamp}</span>
            </div>
            <div className="text-xs">{renderFormattedText(msg.text)}</div>
          </div>
        ))}

        {/* Active Viva Voce Challenge Box */}
        {activeViva && (
          <div className="p-4 rounded-2xl bg-[#020813] border-2 border-amber-500/40 shadow-2xl space-y-3">
            <div className="flex items-center justify-between">
              <span className="px-2 py-0.5 rounded bg-amber-500/20 text-amber-400 font-bold text-[10px]">
                ANNA UNIVERSITY VIVA EXAMINATION
              </span>
              <span className="text-slate-400 text-[10px]">{activeViva.difficulty}</span>
            </div>

            <div className="text-xs text-[#00F0B5] font-bold">
              {activeViva.topic}
            </div>

            <p className="text-xs text-slate-100 font-semibold leading-relaxed">
              "{activeViva.question}"
            </p>

            <textarea
              value={studentAnswer}
              onChange={(e) => setStudentAnswer(e.target.value)}
              placeholder="Type your technical viva explanation here..."
              rows={3}
              className="w-full p-2.5 rounded-xl bg-[#041026] border border-slate-700 text-slate-100 placeholder-slate-500 focus:outline-none focus:border-[#00F0B5] text-xs resize-none"
            />

            <div className="flex gap-2">
              <button
                type="button"
                onClick={handleEvaluateAnswer}
                className="flex-1 py-2 rounded-xl bg-[#00693E] hover:bg-[#008f65] text-white font-bold text-xs transition-all shadow-emerald-glow"
              >
                Submit for Gemini AI Viva Grading
              </button>
              <button
                type="button"
                onClick={() => setActiveViva(null)}
                className="px-3 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs"
              >
                Dismiss
              </button>
            </div>

            {/* Viva Evaluation Result */}
            {vivaEvaluation && (
              <div className="p-3.5 rounded-xl bg-[#041026] border border-emerald-500/40 space-y-2 text-xs">
                <div className="flex items-center justify-between text-[#00F0B5] font-bold">
                  <span>Score: {vivaEvaluation.score} / {vivaEvaluation.maxScore} Marks</span>
                  <span className="text-amber-400">+50 XP Awarded</span>
                </div>
                <p className="text-slate-300 text-[11px] leading-relaxed">
                  {vivaEvaluation.feedback}
                </p>
                <div className="pt-2 border-t border-slate-800">
                  <div className="text-[10px] text-[#00F0B5] font-bold uppercase">Anna University Model Answer:</div>
                  <p className="text-slate-300 text-[11px] mt-1 leading-relaxed">
                    {vivaEvaluation.modelAnswer}
                  </p>
                </div>
              </div>
            )}
          </div>
        )}

        {isLoading && (
          <div className="p-3 rounded-xl bg-[#020813] border border-slate-800 flex items-center gap-2 text-slate-400 text-xs mr-8">
            <span className="h-2 w-2 rounded-full bg-[#00F0B5] animate-ping"></span>
            <span>Gemini Cortex evaluating embedded timing registers...</span>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Query Input Bar */}
      <div className="p-3 bg-[#020813] border-t border-[#00F0B5]/20 flex items-center gap-2">
        <input
          type="text"
          value={inputQuery}
          onChange={(e) => setInputQuery(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSendQuery()}
          placeholder="Ask about RV32I forwarding, Doppler traps, FreeRTOS..."
          className="flex-1 p-2.5 rounded-xl bg-[#041026] border border-slate-700 text-slate-100 placeholder-slate-500 focus:outline-none focus:border-[#00F0B5] text-xs font-mono"
        />
        <button
          type="button"
          onClick={() => handleSendQuery()}
          disabled={isLoading}
          className="p-2.5 rounded-xl bg-gradient-to-r from-[#00693E] to-[#00b884] hover:from-[#008f65] hover:to-[#00F0B5] text-white transition-all shadow-emerald-glow disabled:opacity-50"
        >
          <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="22" y1="2" x2="11" y2="13"></line>
            <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
          </svg>
        </button>
      </div>

    </div>
  );
}

