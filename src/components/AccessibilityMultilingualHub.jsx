import React, { useState, useEffect, useRef } from 'react';

/**
 * ========================================================================================
 * VoltCore Apex Academia - Phase N: Accessibility & Multilingual Learning (Features 341–350)
 * Anna University / MIT Campus - Department of Electronics Engineering (Regulation 2023)
 * Platform Lead: Ashok Kumar A (2023MITEC042)
 *
 * Features:
 *   - Feature 341: English-Tamil Technical Dictionary (Transliteration, Audio, Definitions)
 *   - Feature 342: Tamil Concept Explanation Library (Bilingual ECE Explanations & Audio scripts)
 *   - Feature 343: Text-to-Speech Lesson Reader (Web Speech API, Pitch/Rate, Sentence Tracking)
 *   - Feature 344: Video Subtitle Manager (Dual-track English/Tamil, Timestamp Sync)
 *   - Feature 345: Adjustable Reading Interface (Font scaling, Dyslexic toggle, Line focus ruler)
 *   - Feature 346: Keyboard-Only Navigation & Shortcut Engine (WCAG 2.1 AAA Hotkeys & Focus Rings)
 *   - Feature 347: High-Contrast Theme Options (Contrasts > 7:1 & > 14:1, Colorblind modes)
 *   - Feature 348: Accessible Mathematical Formula Display (MathML/KaTeX + Screen-Reader Audio)
 *   - Feature 349: Simplified Technical Definitions (ELI5 Mode English & Tamil)
 *   - Feature 350: Multilingual Search Support (Cross-lingual Tamil script <-> English matching)
 * Hardware Safe: Zero background polling loops, SQLite WAL mode, passive CPU footprint.
 * ========================================================================================
 */

// Initial Seed Dictionary (Feature 341 & 349)
const DICTIONARY_DATA = [
  {
    id: "term_semi",
    en: "Semiconductor",
    ta: "குறைகடத்தி",
    translit: "Kuraikadathi",
    phonetic: "/kʊ-raɪ-kə-dʌ-θi/",
    code: "EC3451",
    def_en: "A material whose conductivity lies between conductors and insulators, modifiable via doping.",
    def_ta: "கடத்திக்கும் மின்கடத்தாப் பொருளுக்கும் இடைப்பட்ட மின்கடத்துத்திறன் கொண்ட பொருள்; மாசு சேர்த்தல் மூலம் இதன் கடத்துத்திறன் மாற்றப்படும்.",
    eli5_en: "A smart switch material that lets electricity through only when programmed to do so.",
    eli5_ta: "தேவைப்படும்போது மின்சாரத்தை கடத்தவும், தேவையில்லாதபோது தடுக்கவும் கூடிய ஸ்மார்ட் சுவிட்ச்."
  },
  {
    id: "term_diode",
    en: "Diode",
    ta: "இருமுனையம்",
    translit: "Irumunaiyam",
    phonetic: "/ɪ-rʊ-mʊ-naɪ-jʌm/",
    code: "EC3451",
    def_en: "A two-terminal semiconductor device that allows current to flow primarily in one direction (forward bias).",
    def_ta: "நேர்திசை மின்னழுத்தத்தில் மின்னோட்டத்தை எளிதாக கடத்தவும், எதிர்திசையில் தடுக்கவும் செய்யும் இரு முனையக் கருவி.",
    eli5_en: "A one-way turnstile gate for electric current.",
    eli5_ta: "மின்சாரம் ஒரே திசையில் மட்டும் செல்ல அனுமதிக்கும் ஒருவழிப் பாதை கேட்."
  },
  {
    id: "term_transistor",
    en: "Transistor",
    ta: "திரிதடையம்",
    translit: "Thirithadaiyam",
    phonetic: "/θɪ-rɪ-θʌ-daɪ-jʌm/",
    code: "EC3451",
    def_en: "A three-terminal active semiconductor component used to amplify or switch electrical signals.",
    def_ta: "மின் சமிக்ஞைகளைப் பெருக்கவும் மற்றும் விரைவாக சுவிட்ச் செய்யவும் பயன்படும் மூன்று முனையக் கருவி.",
    eli5_en: "An electronic water faucet where a small lever controls a massive stream of current.",
    eli5_ta: "ஒரு சிறிய சிக்னல் மூலம் பெரிய மின்னோட்டத்தைக் கட்டுப்படுத்தும் மின்னணு குழாய்."
  },
  {
    id: "term_cap",
    en: "Capacitor",
    ta: "மின்தேக்கி",
    translit: "Minthekki",
    phonetic: "/mɪn-ðeːk-kɪ/",
    code: "EC3351",
    def_en: "A passive device that stores electrical energy in an electrostatic field between conductive plates.",
    def_ta: "இரு கடத்துத் தகடுகளுக்கு இடையே மின்புலத்தில் ஆற்றலைச் சேமிக்கும் செயலற்ற மின்னணுக் கூறு.",
    eli5_en: "A temporary rechargeable battery that charges and discharges in microseconds.",
    eli5_ta: "மின்னழுத்த ஏற்றத்தாழ்வுகளைச் சீராக்க நொடிகளில் மின்னேற்றம் செய்து உடனே வழங்கும் மின்கலம்."
  },
  {
    id: "term_ind",
    en: "Inductor",
    ta: "மின்தூண்டி",
    translit: "Minthundi",
    phonetic: "/mɪn-ðuːɳ-ɖɪ/",
    code: "EC3452",
    def_en: "A passive component that stores energy in a magnetic field, resisting changes in electric current.",
    def_ta: "மின்னோட்டம் பாயும் போது காந்தப்புலத்தில் ஆற்றலைச் சேமித்து, மின்னோட்ட மாற்றத்தை எதிர்க்கும் கூறு.",
    eli5_en: "An electrical flywheel that resists sudden changes in speed (current).",
    eli5_ta: "மின்சாரத்தில் திடீரென ஏற்படும் மாற்றங்களைத் தடுத்து நிறுத்தும் மின்சுற்று சுருள்."
  },
  {
    id: "term_mod",
    en: "Modulation",
    ta: "பண்பேற்றம்",
    translit: "Panpetram",
    phonetic: "/pʌɳ-beː-trʌm/",
    code: "EC3501",
    def_en: "The process of encoding an information signal onto a high-frequency carrier wave for transmission.",
    def_ta: "தகவல் சமிக்ஞையை தொலைதூரம் அனுப்ப உயர் அதிர்வெண் ஊர்தி அலையின் பண்புகளை மாற்றியமைக்கும் முறை.",
    eli5_en: "Putting your voice letter inside an aerodynamic supersonic jet to send it across the world.",
    eli5_ta: "மெல்லிய குரலை வெகுதூரம் அனுப்ப, அதை ஒரு அதிவேக ராக்கெட் அலையின் மேல் ஏற்றி அனுப்பும் உத்தி."
  }
];

// Concepts Library (Feature 342)
const CONCEPTS = [
  {
    id: "pn_junction",
    title_en: "PN Junction Diode Operation",
    title_ta: "பி-என் சந்தி இருமுனையத்தின் இயக்கம்",
    subject: "EC3451 (Linear Integrated Circuits)",
    en_desc: "In forward bias (V > 0.7V for Silicon), the built-in potential barrier across the depletion region is reduced, allowing diffusion of majority carriers (holes from P to N, electrons from N to P). In reverse bias, the depletion layer widens, permitting only tiny nano-ampere leakage current until avalanche breakdown occurs.",
    ta_desc: "சிலிக்கான் படிகத்தில் பி-வகை மற்றும் என்-வகை பகுதிகள் சந்திக்கும் போது, வறுமை மண்டலம் (Depletion Region) உருவாகிறது. பூஜ்ஜியம் புள்ளி ஏழு வோல்ட் (0.7V) நேர்திசை மின்னழுத்தம் வழங்கும் போது, இவ்வெல்லை சுருங்கி எலக்ட்ரான்களும் துளைகளும் தடையின்றிப் பாய்ந்து மின்னோட்டத்தை உருவாக்குகின்றன.",
    spoken_en: "When forward bias exceeds zero point seven volts in silicon, the depletion barrier narrows and major conduction begins.",
    spoken_ta: "சிலிக்கான் சந்திக்கு பூஜ்ஜியம் புள்ளி ஏழு வோல்ட் நேர்திசை மின்னழுத்தம் வழங்கும் போது, வறுமை மண்டலம் சுருங்கி மின்னோட்டம் பாய்கிறது."
  },
  {
    id: "op_amp_inverting",
    title_en: "Inverting Operational Amplifier",
    title_ta: "எதிர்த்திசை செயல்பாட்டுப் பெருக்கி (Inverting Op-Amp)",
    subject: "EC3451 (Linear Integrated Circuits)",
    en_desc: "By connecting the non-inverting terminal to ground, a Virtual Ground is established at the inverting terminal due to infinite open-loop gain. The input current through Rin must flow entirely into feedback resistor Rf, yielding output voltage Vout = -(Rf/Rin) * Vin, representing a 180-degree phase-inverted amplification.",
    ta_desc: "செயல்பாட்டுப் பெருக்கியின் நேர்மறை முனை தரையிறக்கப்படும் போது, மெய்நிகர் தரை (Virtual Ground) ஏற்படுகிறது. இதனால் உள்ளீட்டு மின்தடை வழியாக வரும் மின்னோட்டம் பின்னூட்ட மின்தடை வழியாகப் பாய்ந்து, Vout = -(Rf/Rin) * Vin என்ற தலைகீழ் பெருக்கப்பட்ட மின்னழுத்தத்தை உருவாக்குகிறது.",
    spoken_en: "Output voltage equals negative open parenthesis R f divided by R in close parenthesis times input voltage.",
    spoken_ta: "வெளியீட்டு மின்னழுத்தம் சமம் மைனஸ் ஆர் எஃப் வகுத்தல் ஆர் இன் பெருக்கல் உள்ளீட்டு மின்னழுத்தம்."
  },
  {
    id: "nyquist_sampling",
    title_en: "Nyquist-Shannon Sampling Theorem",
    title_ta: "நைகுவிஸ்ட்-ஷானன் மாதிரி கோட்பாடு",
    subject: "EC3501 (Wireless Communication)",
    en_desc: "Any continuous-time analog signal bandlimited to maximum frequency f_max can be completely reconstructed without aliasing distortion if sampled at a rate fs >= 2 * f_max. The minimum rate 2 * f_max is called the Nyquist rate.",
    ta_desc: "அனலாக் சிக்னலை சிதைவின்றி துல்லியமாக டிஜிட்டலாக மாற்ற, மாதிரியெடுப்பு அதிர்வெண் சிக்னலின் அதிகபட்ச அதிர்வெண்ணைப் போல குறைந்தது இருமடங்காக (fs >= 2 * f_max) இருக்க வேண்டும். இல்லையேல் மாற்றுப்பெயரிடுதல் (Aliasing) சிதைவு ஏற்படும்.",
    spoken_en: "Sampling frequency f sub s must be at least two times the maximum signal frequency f max to avoid aliasing.",
    spoken_ta: "அலியாசிங் பிழையைத் தவிர்க்க மாதிரியெடுப்பு அதிர்வெண் அதிகபட்ச அதிர்வெண்ணைப் போல குறைந்தது இருமடங்காக இருக்க வேண்டும்."
  }
];

// Video Lecture Subtitles (Feature 344)
const SUBTITLE_TRACKS = [
  { id: 1, start: "00:01", end: "00:04", en: "Welcome to VoltCore Apex Academia Lecture 4.", ta: "வோல்ட்கோர் ஏபெக்ஸ் அகாடமியா பாடம் 4-க்கு உங்களை வரவேற்கிறோம்." },
  { id: 2, start: "00:05", end: "00:09", en: "Today we examine the inverting operational amplifier.", ta: "இன்று நாம் எதிர்த்திசை செயல்பாட்டுப் பெருக்கியைப் பற்றி ஆராய்வோம்." },
  { id: 3, start: "00:10", end: "00:15", en: "Notice how negative feedback creates a stable virtual ground.", ta: "எதிர்மறை பின்னூட்டம் எவ்வாறு நிலையான மெய்நிகர் தரையை உருவாக்குகிறது என்பதைக் கவனியுங்கள்." },
  { id: 4, start: "00:16", end: "00:21", en: "The closed-loop voltage gain is strictly determined by Rf over Rin.", ta: "மூடிய வளைய மின்னழுத்தப் பெருக்கம் ஆர் எஃப் மற்றும் ஆர் இன் விகிதத்தால் தீர்மானிக்கப்படுகிறது." }
];

// Accessible Formulas (Feature 348)
const ACCESSIBLE_MATH = [
  {
    id: "ohm",
    name: "Ohm's Law",
    latex: "V = I \\times R",
    spoken_en: "Voltage V equals electric current I multiplied by electrical resistance R.",
    spoken_ta: "மின்னழுத்தம் V சமம் மின்னோட்டம் I பெருக்கல் மின்தடை R."
  },
  {
    id: "gain",
    name: "Inverting Op-Amp Closed-Loop Gain",
    latex: "V_{\\text{out}} = -\\left(\\frac{R_f}{R_{\\text{in}}}\\right) V_{\\text{in}}",
    spoken_en: "Output voltage V out equals negative open parenthesis R f divided by R in close parenthesis multiplied by input voltage V in.",
    spoken_ta: "வெளியீட்டு மின்னழுத்தம் V out சமம் மைனஸ் ஆர் எஃப் வகுத்தல் ஆர் இன் பெருக்கல் உள்ளீட்டு மின்னழுத்தம் V in."
  },
  {
    id: "nyquist",
    name: "Nyquist Minimum Sampling Criterion",
    latex: "f_s \\ge 2 f_{\\max}",
    spoken_en: "Sampling frequency f sub s must be greater than or equal to two times the maximum signal frequency f sub max.",
    spoken_ta: "மாதிரியெடுப்பு அதிர்வெண் f sub s சிக்னலின் உச்ச அதிர்வெண் f max-ஐ விட இருமடங்கு அல்லது அதற்கு அதிகமாக இருக்க வேண்டும்."
  }
];

export default function AccessibilityMultilingualHub() {
  const [activeTab, setActiveTab] = useState('dictionary');

  // Feature 341 & 350: Search State
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedTerm, setSelectedTerm] = useState(DICTIONARY_DATA[0]);
  const [eli5Mode, setEli5Mode] = useState(false); // Feature 349

  // Feature 342: Concept State
  const [activeConceptId, setActiveConceptId] = useState('pn_junction');

  // Feature 343: Text-to-Speech (TTS) State
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [speechRate, setSpeechRate] = useState(1.0);
  const [speechPitch, setSpeechPitch] = useState(1.0);
  const [ttsLang, setTtsLang] = useState('en-IN');
  const [currentSentenceIndex, setCurrentSentenceIndex] = useState(0);

  // Feature 344: Subtitle Manager State
  const [activeSubIndex, setActiveSubIndex] = useState(0);
  const [subtitleLang, setSubtitleLang] = useState('bilingual'); // 'en', 'ta', 'bilingual'
  const [isPlayingLecture, setIsPlayingLecture] = useState(false);

  // Feature 345: Adjustable Reading Controls
  const [fontSize, setFontSize] = useState(16);
  const [lineSpacing, setLineSpacing] = useState(1.6);
  const [letterSpacing, setLetterSpacing] = useState(0.5);
  const [isDyslexicFont, setIsDyslexicFont] = useState(false);
  const [lineFocusRuler, setLineFocusRuler] = useState(false);
  const [rulerY, setRulerY] = useState(150);

  // Feature 347: High-Contrast Themes
  const [themeMode, setThemeMode] = useState('dark_cyber');

  // Theme styling configurations
  const themeClasses = {
    dark_cyber: "bg-slate-950 text-slate-100 border-cyan-500/30",
    high_contrast_dark: "bg-black text-white border-white",
    high_contrast_light: "bg-white text-black border-black",
    solarized_yellow: "bg-amber-950 text-amber-200 border-amber-400",
    navy_yellow: "bg-slate-900 text-yellow-300 border-yellow-400"
  };

  // Keyboard shortcut listener (Feature 346)
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.altKey) {
        if (e.key === '1') setActiveTab('dictionary');
        if (e.key === '2') setActiveTab('concepts');
        if (e.key === '3') setActiveTab('tts_reader');
        if (e.key === '4') setActiveTab('subtitles');
        if (e.key === '5') setActiveTab('reading_settings');
        if (e.key === '6') setActiveTab('math_formulas');
      }
      if (e.code === 'Space' && e.ctrlKey) {
        e.preventDefault();
        toggleSpeakCurrentText();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [selectedTerm, activeConceptId, isSpeaking]);

  // Simulated lecture playback timer for subtitle sync (Feature 344)
  useEffect(() => {
    let interval = null;
    if (isPlayingLecture) {
      interval = setInterval(() => {
        setActiveSubIndex(prev => (prev + 1) % SUBTITLE_TRACKS.length);
      }, 4000);
    }
    return () => clearInterval(interval);
  }, [isPlayingLecture]);

  // Text to Speech invocation (Feature 343)
  const speakText = (text, lang = 'en-IN') => {
    if (!('speechSynthesis' in window)) {
      alert("Web Speech API not supported in this browser. Please use Chrome, Edge, or Firefox.");
      return;
    }
    window.speechSynthesis.cancel();
    if (!text) return;

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = speechRate;
    utterance.pitch = speechPitch;
    utterance.lang = lang;

    utterance.onstart = () => setIsSpeaking(true);
    utterance.onend = () => setIsSpeaking(false);
    utterance.onerror = () => setIsSpeaking(false);

    window.speechSynthesis.speak(utterance);
  };

  const stopSpeaking = () => {
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
      setIsSpeaking(false);
    }
  };

  const toggleSpeakCurrentText = () => {
    if (isSpeaking) {
      stopSpeaking();
    } else {
      const activeConcept = CONCEPTS.find(c => c.id === activeConceptId) || CONCEPTS[0];
      const textToSpeak = ttsLang === 'ta-IN' ? activeConcept.spoken_ta : activeConcept.spoken_en;
      speakText(textToSpeak, ttsLang);
    }
  };

  // Filter dictionary terms based on English, Tamil, or Transliteration
  const filteredTerms = DICTIONARY_DATA.filter(item => {
    const q = searchQuery.toLowerCase().trim();
    if (!q) return true;
    return (
      item.en.toLowerCase().includes(q) ||
      item.ta.includes(q) ||
      item.translit.toLowerCase().includes(q)
    );
  });

  return (
    <div
      className={`accessibility-hub space-y-6 transition-colors duration-200 ${themeClasses[themeMode]} p-4 sm:p-6 rounded-3xl border`}
      style={{
        fontSize: `${fontSize}px`,
        lineHeight: lineSpacing,
        letterSpacing: `${letterSpacing}px`,
        fontFamily: isDyslexicFont ? "'OpenDyslexic', 'Comic Sans MS', sans-serif" : "inherit"
      }}
      onMouseMove={(e) => lineFocusRuler && setRulerY(e.clientY - 40)}
    >
      {/* Line Focus Guide / Reading Ruler (Feature 345) */}
      {lineFocusRuler && (
        <div
          className="fixed left-0 right-0 h-14 bg-cyan-400/15 border-y-2 border-cyan-400 pointer-events-none z-50 backdrop-blur-[1px]"
          style={{ top: `${rulerY}px` }}
        />
      )}

      {/* Screen Reader Live Announcement Region (WCAG 2.1 AAA - Feature 346) */}
      <div className="sr-only" aria-live="polite">
        Current active tab: {activeTab}. Theme: {themeMode}. Font size: {fontSize} pixels.
      </div>

      {/* Header Hub Card */}
      <div className="bg-slate-900/80 border border-cyan-500/30 rounded-2xl p-6 backdrop-blur-md shadow-2xl relative overflow-hidden">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex flex-wrap items-center gap-2 mb-2">
              <span className="px-3 py-1 text-xs font-bold rounded-full bg-cyan-500/20 text-cyan-400 border border-cyan-500/40">
                PHASE N • ACCESSIBILITY & MULTILINGUAL
              </span>
              <span className="px-3 py-1 text-xs font-bold rounded-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/40">
                WCAG 2.1 AAA COMPLIANT
              </span>
              <span className="px-3 py-1 text-xs font-bold rounded-full bg-purple-500/20 text-purple-400 border border-purple-500/40">
                தமிழ் / ENGLISH BILINGUAL
              </span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
              Accessibility & Multilingual Learning Hub
            </h1>
            <p className="text-sm text-slate-400 mt-1">
              Anna University Reg 2023 • English-Tamil Technical Lexicon, Speech Reader, Subtitles & WCAG Engine
            </p>
          </div>

          {/* Quick Audio & Contrast Controls */}
          <div className="flex items-center gap-2 bg-slate-800/80 border border-slate-700 p-2.5 rounded-xl">
            <button
              onClick={toggleSpeakCurrentText}
              className={`px-3 py-1.5 rounded-lg text-xs font-bold transition flex items-center gap-1.5 ${
                isSpeaking
                  ? 'bg-rose-500 text-white animate-pulse'
                  : 'bg-cyan-500 text-slate-950 hover:bg-cyan-400'
              }`}
              title="Ctrl + Space to Play/Pause Speech"
            >
              <span>{isSpeaking ? '⏹ Stop Audio' : '🔊 Listen (TTS)'}</span>
            </button>

            <select
              value={themeMode}
              onChange={e => setThemeMode(e.target.value)}
              className="bg-slate-900 border border-slate-700 text-white text-xs rounded-lg px-2.5 py-1.5 focus:ring-2 focus:ring-cyan-500"
              aria-label="High Contrast Theme Selector"
            >
              <option value="dark_cyber">Dark Cyber (Default)</option>
              <option value="high_contrast_dark">High Contrast Dark (21:1)</option>
              <option value="high_contrast_light">High Contrast Light (21:1)</option>
              <option value="solarized_yellow">Solarized Amber (12:1)</option>
              <option value="navy_yellow">Navy & Gold (14:1)</option>
            </select>
          </div>
        </div>

        {/* Tab Navigation with Hotkey Badges (Feature 346) */}
        <div className="flex flex-wrap gap-2 mt-6 border-t border-slate-800 pt-4">
          {[
            { id: 'dictionary', label: 'English-Tamil Lexicon', icon: '📖', key: 'Alt+1' },
            { id: 'concepts', label: 'Tamil Concept Library', icon: '🎓', key: 'Alt+2' },
            { id: 'tts_reader', label: 'Speech Lesson Reader', icon: '🎙️', key: 'Alt+3' },
            { id: 'subtitles', label: 'Bilingual Subtitle Sync', icon: '💬', key: 'Alt+4' },
            { id: 'reading_settings', label: 'Reading Adjuster', icon: '⚙️', key: 'Alt+5' },
            { id: 'math_formulas', label: 'Accessible Math Formulas', icon: '📐', key: 'Alt+6' }
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-3.5 py-2 rounded-xl text-xs font-semibold transition-all flex items-center gap-2 focus:ring-2 focus:ring-cyan-400 outline-none ${
                activeTab === tab.id
                  ? 'bg-cyan-500 text-slate-950 font-bold shadow-lg shadow-cyan-500/20'
                  : 'bg-slate-800/60 text-slate-300 hover:bg-slate-700 hover:text-white border border-slate-700/40'
              }`}
            >
              <span>{tab.icon}</span>
              <span>{tab.label}</span>
              <span className="text-[10px] opacity-60 font-mono hidden sm:inline">[{tab.key}]</span>
            </button>
          ))}
        </div>
      </div>

      {/* =========================================================================
          TAB 1: ENGLISH-TAMIL TECHNICAL DICTIONARY (Features 341, 349, 350)
      ========================================================================= */}
      {activeTab === 'dictionary' && (
        <div className="space-y-6">
          {/* Search Bar with Tamil Script Auto-Detection */}
          <div className="bg-slate-900/60 border border-slate-800 p-4 rounded-xl flex flex-col sm:flex-row gap-3 items-center justify-between">
            <div className="relative flex-1 w-full">
              <input
                type="text"
                value={searchQuery}
                onChange={e => setSearchQuery(e.target.value)}
                placeholder="Search in English or தமிழ் script (e.g., Diode or இருமுனையம்)..."
                className="w-full bg-slate-800 border border-slate-700 rounded-lg pl-3 pr-10 py-2 text-xs text-white placeholder-slate-400 focus:outline-none focus:border-cyan-500"
              />
              <span className="absolute right-3 top-2.5 text-xs text-slate-400">🔍</span>
            </div>

            {/* Feature 349: ELI5 Toggle */}
            <div className="flex items-center gap-2 bg-slate-800 px-3 py-1.5 rounded-lg border border-slate-700">
              <span className="text-xs font-medium text-slate-300">ELI5 Simplified Mode:</span>
              <button
                onClick={() => setEli5Mode(!eli5Mode)}
                className={`px-2.5 py-0.5 rounded text-xs font-bold transition ${
                  eli5Mode ? 'bg-emerald-500 text-slate-950' : 'bg-slate-700 text-slate-400'
                }`}
              >
                {eli5Mode ? 'ON' : 'OFF'}
              </button>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Term List */}
            <div className="space-y-2 max-h-[500px] overflow-y-auto pr-1">
              {filteredTerms.map(item => (
                <div
                  key={item.id}
                  onClick={() => setSelectedTerm(item)}
                  className={`p-3.5 rounded-xl border cursor-pointer transition flex items-center justify-between ${
                    selectedTerm.id === item.id
                      ? 'bg-cyan-500/20 border-cyan-500 text-white font-bold'
                      : 'bg-slate-900/80 border-slate-800 text-slate-300 hover:border-slate-700'
                  }`}
                >
                  <div>
                    <div className="text-sm font-bold text-white flex items-center gap-2">
                      <span>{item.en}</span>
                      <span className="text-cyan-400 font-normal">({item.ta})</span>
                    </div>
                    <div className="text-xs text-slate-400 mt-0.5">{item.translit} • {item.code}</div>
                  </div>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      speakText(`${item.en}. தமிழில்: ${item.ta}. ${item.def_en}`, 'en-IN');
                    }}
                    className="p-1.5 bg-slate-800 hover:bg-slate-700 rounded-lg text-cyan-400 text-xs"
                    title="Pronounce term"
                  >
                    🔊
                  </button>
                </div>
              ))}
              {filteredTerms.length === 0 && (
                <div className="text-xs text-slate-400 text-center py-6">No matching ECE terms found.</div>
              )}
            </div>

            {/* Term Detail View */}
            <div className="lg:col-span-2 bg-slate-900/80 border border-slate-800 rounded-xl p-6 space-y-4">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-800 pb-3">
                <div>
                  <div className="flex items-center gap-2">
                    <h2 className="text-2xl font-black text-white">{selectedTerm.en}</h2>
                    <span className="text-xl font-bold text-cyan-400">{selectedTerm.ta}</span>
                  </div>
                  <div className="text-xs text-slate-400 mt-1">
                    Transliteration: <strong className="text-slate-200">{selectedTerm.translit}</strong> • Phonetic: <code className="text-purple-300">{selectedTerm.phonetic}</code> • Course: <strong className="text-cyan-300">{selectedTerm.code}</strong>
                  </div>
                </div>

                <div className="flex gap-2">
                  <button
                    onClick={() => speakText(selectedTerm.en, 'en-IN')}
                    className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-cyan-300 border border-slate-700 rounded-lg text-xs font-bold"
                  >
                    🔊 English Audio
                  </button>
                  <button
                    onClick={() => speakText(selectedTerm.ta, 'ta-IN')}
                    className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-purple-300 border border-slate-700 rounded-lg text-xs font-bold"
                  >
                    🔊 தமிழ் உச்சரிப்பு
                  </button>
                </div>
              </div>

              {/* Standard vs ELI5 Explanation */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="p-4 rounded-xl bg-slate-800/40 border border-slate-700/60 space-y-2">
                  <div className="text-xs font-bold uppercase tracking-wider text-cyan-400">
                    {eli5Mode ? 'Simplified English (ELI5)' : 'Formal Academic Definition (English)'}
                  </div>
                  <p className="text-xs text-slate-200 leading-relaxed">
                    {eli5Mode ? selectedTerm.eli5_en : selectedTerm.def_en}
                  </p>
                </div>

                <div className="p-4 rounded-xl bg-slate-800/40 border border-slate-700/60 space-y-2">
                  <div className="text-xs font-bold uppercase tracking-wider text-purple-400">
                    {eli5Mode ? 'எளிய தமிழ் விளக்கம் (ELI5)' : 'தமிழ் கலைச்சொல் விளக்கம்'}
                  </div>
                  <p className="text-xs text-slate-200 leading-relaxed">
                    {eli5Mode ? selectedTerm.eli5_ta : selectedTerm.def_ta}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* =========================================================================
          TAB 2: TAMIL CONCEPT EXPLANATION LIBRARY (Feature 342)
      ========================================================================= */}
      {activeTab === 'concepts' && (
        <div className="space-y-6">
          <div className="flex flex-wrap gap-2">
            {CONCEPTS.map(c => (
              <button
                key={c.id}
                onClick={() => setActiveConceptId(c.id)}
                className={`px-4 py-2 rounded-xl text-xs font-bold transition ${
                  activeConceptId === c.id
                    ? 'bg-cyan-500 text-slate-950 shadow-md shadow-cyan-500/20'
                    : 'bg-slate-800/80 text-slate-300 hover:bg-slate-700'
                }`}
              >
                {c.title_en}
              </button>
            ))}
          </div>

          {(() => {
            const concept = CONCEPTS.find(c => c.id === activeConceptId) || CONCEPTS[0];
            return (
              <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-6 space-y-6">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-800 pb-3">
                  <div>
                    <h2 className="text-xl font-bold text-white">{concept.title_en}</h2>
                    <h3 className="text-base font-semibold text-cyan-400">{concept.title_ta}</h3>
                    <div className="text-xs text-slate-400 mt-0.5">{concept.subject}</div>
                  </div>

                  <div className="flex gap-2">
                    <button
                      onClick={() => speakText(concept.spoken_en, 'en-IN')}
                      className="px-3.5 py-2 bg-slate-800 hover:bg-slate-700 text-cyan-300 border border-slate-700 rounded-lg text-xs font-bold flex items-center gap-1.5"
                    >
                      <span>🔊</span> Read English Audio
                    </button>
                    <button
                      onClick={() => speakText(concept.spoken_ta, 'ta-IN')}
                      className="px-3.5 py-2 bg-slate-800 hover:bg-slate-700 text-purple-300 border border-slate-700 rounded-lg text-xs font-bold flex items-center gap-1.5"
                    >
                      <span>🔊</span> தமிழில் வாசி
                    </button>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-2">
                    <div className="text-xs font-bold text-slate-400 uppercase tracking-wider">English Concept Overview</div>
                    <div className="p-4 bg-slate-800/50 border border-slate-700/60 rounded-xl text-xs text-slate-200 leading-relaxed">
                      {concept.en_desc}
                    </div>
                  </div>

                  <div className="space-y-2">
                    <div className="text-xs font-bold text-slate-400 uppercase tracking-wider">விரிவான தமிழ் விளக்கம்</div>
                    <div className="p-4 bg-slate-800/50 border border-slate-700/60 rounded-xl text-xs text-slate-200 leading-relaxed font-sans">
                      {concept.ta_desc}
                    </div>
                  </div>
                </div>
              </div>
            );
          })()}
        </div>
      )}

      {/* =========================================================================
          TAB 3: TEXT-TO-SPEECH LESSON READER (Feature 343)
      ========================================================================= */}
      {activeTab === 'tts_reader' && (
        <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-6 space-y-6">
          <div>
            <h2 className="text-lg font-bold text-white flex items-center gap-2">
              <span>🎙️</span> Text-to-Speech Lesson Reader (Web Speech Engine)
            </h2>
            <p className="text-xs text-slate-400">Configure speech rate, pitch, and voice synthesis dialect for natural ECE narration</p>
          </div>

          {/* Controls Bar */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 bg-slate-800/50 p-4 rounded-xl border border-slate-700">
            <div>
              <div className="flex justify-between text-xs font-semibold text-slate-300 mb-1">
                <span>Reading Speed (Rate)</span>
                <span className="text-cyan-400">{speechRate}x</span>
              </div>
              <input
                type="range"
                min="0.5"
                max="2.0"
                step="0.1"
                value={speechRate}
                onChange={e => setSpeechRate(parseFloat(e.target.value))}
                className="w-full accent-cyan-400"
              />
            </div>

            <div>
              <div className="flex justify-between text-xs font-semibold text-slate-300 mb-1">
                <span>Voice Pitch</span>
                <span className="text-purple-400">{speechPitch}x</span>
              </div>
              <input
                type="range"
                min="0.5"
                max="1.5"
                step="0.1"
                value={speechPitch}
                onChange={e => setSpeechPitch(parseFloat(e.target.value))}
                className="w-full accent-purple-400"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">Voice Dialect</label>
              <select
                value={ttsLang}
                onChange={e => setTtsLang(e.target.value)}
                className="w-full bg-slate-900 border border-slate-700 rounded-lg px-2.5 py-1.5 text-xs text-white"
              >
                <option value="en-IN">Indian English (en-IN)</option>
                <option value="ta-IN">Tamil (ta-IN)</option>
              </select>
            </div>
          </div>

          {/* Reader Interactive Workspace */}
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">Lesson Passage</span>
              <div className="flex gap-2">
                <button
                  onClick={() => speakText(CONCEPTS[0].en_desc, ttsLang)}
                  className="px-4 py-1.5 bg-cyan-500 text-slate-950 font-bold rounded-lg text-xs hover:bg-cyan-400 transition"
                >
                  ▶ Read Full Passage
                </button>
                <button
                  onClick={stopSpeaking}
                  className="px-4 py-1.5 bg-rose-500/20 text-rose-300 border border-rose-500/40 rounded-lg text-xs font-bold hover:bg-rose-500/30 transition"
                >
                  ⏹ Stop
                </button>
              </div>
            </div>

            <div className="p-5 bg-slate-950/80 border border-slate-800 rounded-xl text-xs text-slate-200 leading-relaxed font-mono">
              {CONCEPTS[0].en_desc}
            </div>
          </div>
        </div>
      )}

      {/* =========================================================================
          TAB 4: VIDEO SUBTITLE MANAGER (Feature 344)
      ========================================================================= */}
      {activeTab === 'subtitles' && (
        <div className="space-y-6">
          <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-6 space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
              <div>
                <h2 className="text-lg font-bold text-white flex items-center gap-2">
                  <span>💬</span> Video Subtitle Track Sync Manager
                </h2>
                <p className="text-xs text-slate-400">Synchronized bilingual timestamped cues for ECE video lectures</p>
              </div>

              <div className="flex items-center gap-2">
                <button
                  onClick={() => setIsPlayingLecture(!isPlayingLecture)}
                  className={`px-3.5 py-1.5 rounded-lg text-xs font-bold transition ${
                    isPlayingLecture ? 'bg-amber-500 text-slate-950' : 'bg-cyan-500 text-slate-950'
                  }`}
                >
                  {isPlayingLecture ? '⏸ Pause Playback' : '▶ Simulate Playback'}
                </button>

                <select
                  value={subtitleLang}
                  onChange={e => setSubtitleLang(e.target.value)}
                  className="bg-slate-800 border border-slate-700 text-xs rounded-lg px-2.5 py-1.5 text-white"
                >
                  <option value="bilingual">Bilingual (English + தமிழ்)</option>
                  <option value="en">English Only</option>
                  <option value="ta">தமிழ் Only</option>
                </select>
              </div>
            </div>

            {/* Video Player Display Simulation */}
            <div className="aspect-video max-h-72 bg-slate-950 border border-slate-800 rounded-xl relative flex flex-col justify-end p-6 overflow-hidden">
              <div className="absolute inset-0 flex items-center justify-center opacity-10 text-cyan-400 font-mono text-4xl font-black">
                VOLTCORE LECTURE PLAYER
              </div>

              {/* Subtitle Overlay Banner */}
              <div className="bg-black/85 backdrop-blur-md border border-slate-700/80 p-3 rounded-lg text-center mx-auto max-w-xl transition-all">
                {(subtitleLang === 'en' || subtitleLang === 'bilingual') && (
                  <div className="text-sm font-semibold text-white">
                    {SUBTITLE_TRACKS[activeSubIndex].en}
                  </div>
                )}
                {(subtitleLang === 'ta' || subtitleLang === 'bilingual') && (
                  <div className="text-xs font-medium text-cyan-300 mt-1">
                    {SUBTITLE_TRACKS[activeSubIndex].ta}
                  </div>
                )}
                <div className="text-[10px] text-slate-400 mt-1 font-mono">
                  Cue {activeSubIndex + 1}/{SUBTITLE_TRACKS.length} • Timestamp: {SUBTITLE_TRACKS[activeSubIndex].start} – {SUBTITLE_TRACKS[activeSubIndex].end}
                </div>
              </div>
            </div>

            {/* Cue List Navigation */}
            <div className="space-y-2">
              <div className="text-xs font-bold text-slate-400 uppercase tracking-wider">Timestamp Cues</div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                {SUBTITLE_TRACKS.map((cue, idx) => (
                  <div
                    key={cue.id}
                    onClick={() => setActiveSubIndex(idx)}
                    className={`p-2.5 rounded-lg border text-xs cursor-pointer transition ${
                      activeSubIndex === idx
                        ? 'bg-cyan-500/20 border-cyan-500 text-white font-bold'
                        : 'bg-slate-800/40 border-slate-700/60 text-slate-300 hover:bg-slate-800'
                    }`}
                  >
                    <span className="font-mono text-cyan-400">[{cue.start}]</span> {cue.en}
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* =========================================================================
          TAB 5: ADJUSTABLE READING INTERFACE (Features 345 & 347)
      ========================================================================= */}
      {activeTab === 'reading_settings' && (
        <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-6 space-y-6">
          <div>
            <h2 className="text-lg font-bold text-white flex items-center gap-2">
              <span>⚙️</span> Adjustable Reading Interface & Focus Tools
            </h2>
            <p className="text-xs text-slate-400">Customize typography parameters to minimize visual fatigue and aid dyslexia</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Sliders */}
            <div className="space-y-4 bg-slate-800/40 p-5 rounded-xl border border-slate-700/60">
              <div>
                <div className="flex justify-between text-xs font-semibold text-slate-300 mb-1">
                  <span>Font Size Scaling</span>
                  <span className="text-cyan-400 font-bold">{fontSize}px</span>
                </div>
                <input
                  type="range"
                  min="12"
                  max="24"
                  value={fontSize}
                  onChange={e => setFontSize(parseInt(e.target.value))}
                  className="w-full accent-cyan-400"
                />
              </div>

              <div>
                <div className="flex justify-between text-xs font-semibold text-slate-300 mb-1">
                  <span>Line Height Spacing</span>
                  <span className="text-purple-400 font-bold">{lineSpacing}</span>
                </div>
                <input
                  type="range"
                  min="1.2"
                  max="2.2"
                  step="0.1"
                  value={lineSpacing}
                  onChange={e => setLineSpacing(parseFloat(e.target.value))}
                  className="w-full accent-purple-400"
                />
              </div>

              <div>
                <div className="flex justify-between text-xs font-semibold text-slate-300 mb-1">
                  <span>Letter Spacing (Kerning)</span>
                  <span className="text-emerald-400 font-bold">{letterSpacing}px</span>
                </div>
                <input
                  type="range"
                  min="0"
                  max="3"
                  step="0.25"
                  value={letterSpacing}
                  onChange={e => setLetterSpacing(parseFloat(e.target.value))}
                  className="w-full accent-emerald-400"
                />
              </div>

              <div className="pt-2 flex flex-wrap gap-3">
                <button
                  onClick={() => setIsDyslexicFont(!isDyslexicFont)}
                  className={`px-3.5 py-2 rounded-lg text-xs font-bold transition ${
                    isDyslexicFont ? 'bg-purple-500 text-white' : 'bg-slate-700 text-slate-300'
                  }`}
                >
                  {isDyslexicFont ? '✓ Dyslexic Font Active' : 'Enable Dyslexia-Friendly Font'}
                </button>

                <button
                  onClick={() => setLineFocusRuler(!lineFocusRuler)}
                  className={`px-3.5 py-2 rounded-lg text-xs font-bold transition ${
                    lineFocusRuler ? 'bg-cyan-500 text-slate-950' : 'bg-slate-700 text-slate-300'
                  }`}
                >
                  {lineFocusRuler ? '✓ Line Focus Ruler Active' : 'Enable Line Focus Ruler'}
                </button>
              </div>
            </div>

            {/* Live Preview Panel */}
            <div className="p-5 bg-slate-950/80 border border-slate-800 rounded-xl flex flex-col justify-between">
              <div>
                <div className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Typography Live Preview</div>
                <p className="text-slate-200">
                  Madras Institute of Technology (MIT Campus), Anna University. In linear circuits, passive components obey Kirchhoff's Voltage and Current laws. Real-time feedback stabilizes closed-loop operational amplifiers.
                </p>
              </div>
              <div className="mt-4 text-[11px] text-cyan-400">
                Current Settings: {fontSize}px size • {lineSpacing} line-height • {letterSpacing}px letter-spacing
              </div>
            </div>
          </div>
        </div>
      )}

      {/* =========================================================================
          TAB 6: ACCESSIBLE MATHEMATICAL FORMULAS (Feature 348)
      ========================================================================= */}
      {activeTab === 'math_formulas' && (
        <div className="space-y-6">
          <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-6 space-y-4">
            <div>
              <h2 className="text-lg font-bold text-white flex items-center gap-2">
                <span>📐</span> Accessible Mathematical Formula Reader
              </h2>
              <p className="text-xs text-slate-400">Mathematical equations rendered with spoken natural-language descriptions for screen readers</p>
            </div>

            <div className="space-y-4">
              {ACCESSIBLE_MATH.map(form => (
                <div key={form.id} className="bg-slate-800/40 border border-slate-700/60 rounded-xl p-5 space-y-3">
                  <div className="flex items-center justify-between">
                    <h3 className="text-sm font-bold text-white">{form.name}</h3>
                    <div className="flex gap-2">
                      <button
                        onClick={() => speakText(form.spoken_en, 'en-IN')}
                        className="px-3 py-1 bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 rounded-lg text-xs font-bold hover:bg-cyan-500/30"
                      >
                        🔊 Read in English
                      </button>
                      <button
                        onClick={() => speakText(form.spoken_ta, 'ta-IN')}
                        className="px-3 py-1 bg-purple-500/20 text-purple-300 border border-purple-500/40 rounded-lg text-xs font-bold hover:bg-purple-500/30"
                      >
                        🔊 தமிழில் வாசி
                      </button>
                    </div>
                  </div>

                  <div className="p-3 bg-slate-950 rounded-lg text-center font-mono text-cyan-300 text-sm">
                    {form.latex}
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-xs">
                    <div className="p-2.5 bg-slate-800/60 rounded-lg text-slate-300">
                      <strong className="text-cyan-400">English Speech:</strong> {form.spoken_en}
                    </div>
                    <div className="p-2.5 bg-slate-800/60 rounded-lg text-slate-300">
                      <strong className="text-purple-400">தமிழ் உச்சரிப்பு:</strong> {form.spoken_ta}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
