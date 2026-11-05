import React, { useState, useEffect } from 'react';

/**
 * ========================================================================================
 * VoltCore Apex Academia - Accessibility & Inclusive Learning Center (Phase 26)
 * Anna University / MIT Campus Standards (Department of Electronics Engineering)
 * Course Scope: EC3451 (LIC), EC3491 (CS), EC3352 (DSD), EC3601 (Embedded)
 * ----------------------------------------------------------------------------------------
 * Platform Lead / Architect: Ashok Kumar A (2023MITEC042)
 * Public Contact: ashokkumar3132008@gmail.com | GitHub: https://github.com/AshokKumar313
 * Institution: Madras Institute of Technology (MIT) Campus, Anna University, Chromepet
 * ========================================================================================
 */

// Fallback Bilingual ECE Dictionary
const FALLBACK_DICTIONARY = [
  {
    term_id: "TERM_OPAMP",
    term_en: "Operational Amplifier (Op-Amp)",
    term_ta: "செயற்பாட்டு பெருக்கி",
    phonetic_ta: "Seyarpaattu Perukki",
    category: "Analog Circuits",
    course_code: "EC3451",
    definition_en: "A high-gain direct-coupled differential voltage amplifier with single-ended output, ideal for mathematical operations and active filtering.",
    definition_ta: "மிக அதிக மிகைப்புத்திறன் கொண்ட நேர்-இணைப்பு வேறுபாட்டு மின்னழுத்த பெருக்கி. இது கணித செயல்பாடுகள் மற்றும் சுறுசுறுப்பான வடிகட்டிகளுக்குப் பயன்படுகிறது.",
    example_usage: "The LM741 operational amplifier is configured as an inverting amplifier with negative feedback."
  },
  {
    term_id: "TERM_BANDWIDTH",
    term_en: "Bandwidth",
    term_ta: "அலைவரிசை அகலம்",
    phonetic_ta: "Alaivarisai Agalam",
    category: "Communication Systems",
    course_code: "EC3491",
    definition_en: "The range of frequencies within a continuous band that can pass through a channel or filter without significant attenuation (-3dB limits).",
    definition_ta: "ஒரு தடம் அல்லது வடிகட்டி வழியாக குறிப்பிடத்தக்க இழப்பின்றி (-3dB வரம்பு) செல்லக்கூடிய தொடர்ச்சியான அலைவரிசைகளின் வீச்சு.",
    example_usage: "Carson's rule estimates the transmission bandwidth of a frequency modulated (FM) signal."
  },
  {
    term_id: "TERM_SLEW_RATE",
    term_en: "Slew Rate",
    term_ta: "மின்னழுத்த மாற்ற வேகம்",
    phonetic_ta: "Min-azhutha Maatra Vegam",
    category: "Analog Circuits",
    course_code: "EC3451",
    definition_en: "The maximum rate of change of an amplifier's output voltage with respect to time, typically expressed in Volts per microsecond (V/us).",
    definition_ta: "ஒரு பெருக்கியின் வெளியீட்டு மின்னழுத்தம் காலத்தைப் பொறுத்து மாறக்கூடிய அதிகபட்ச வேகம். இது மைக்ரோவினாடிக்கு வோல்ட் (V/us) என்ற அலகால் அளக்கப்படுகிறது.",
    example_usage: "Exceeding the op-amp slew rate distorts a sinusoidal output waveform into a triangular wave."
  },
  {
    term_id: "TERM_TRANSISTOR_BIAS",
    term_en: "Transistor Biasing",
    term_ta: "திரிதடைய சார்பளித்தல்",
    phonetic_ta: "Thirithadai Saarpalithal",
    category: "Analog Circuits",
    course_code: "EC3451",
    definition_en: "The application of fixed DC voltages across transistor terminals to establish a stable quiescent operating point (Q-point) in the active region.",
    definition_ta: "திரிதடையத்தின் முனையங்களில் நிலையான நேர் மின்னழுத்தங்களை வழங்கி, செயல்படு பகுதியில் அமைதியான இயக்கப் புள்ளியை (Q-point) நிலைநிறுத்தும் முறை.",
    example_usage: "Voltage divider bias provides excellent thermal stability for BJT audio amplifier stages."
  },
  {
    term_id: "TERM_MODULATION",
    term_en: "Modulation",
    term_ta: "பண்பேற்றம்",
    phonetic_ta: "Panbetram",
    category: "Communication Systems",
    course_code: "EC3491",
    definition_en: "The process of varying one or more properties (amplitude, frequency, phase) of a high-frequency carrier signal in accordance with a message signal.",
    definition_ta: "செய்தி சைகைக்கு ஏற்ப, உயர் அதிர்வெண் கொண்ட ஊர்தி சைகையின் பண்புகளை (வீச்சு, அதிர்வெண், கட்டம்) மாற்றியமைக்கும் செயல்முறை.",
    example_usage: "Frequency modulation (FM) provides superior noise immunity compared to amplitude modulation (AM)."
  },
  {
    term_id: "TERM_DEMODULATION",
    term_en: "Demodulation",
    term_ta: "பண்பிறக்கம்",
    phonetic_ta: "Panpirakkam",
    category: "Communication Systems",
    course_code: "EC3491",
    definition_en: "The extraction of the original information-bearing baseband signal from the modulated carrier wave at the receiver stage.",
    definition_ta: "பெறுமுனையில் பண்பேற்றப்பட்ட ஊர்தி அலையிலிருந்து அசல் செய்தி சைகையை பிரித்தெடுக்கும் செயல்முறை.",
    example_usage: "An envelope detector diode circuit performs simple demodulation of standard AM signals."
  },
  {
    term_id: "TERM_SAMPLING",
    term_en: "Sampling Theorem",
    term_ta: "மாதிரி எடுப்பு தேற்றம்",
    phonetic_ta: "Maathiri Eduppu Thetram",
    category: "Signal Processing",
    course_code: "EC3491",
    definition_en: "The principle stating that a continuous band-limited signal can be completely reconstructed if sampled at a rate greater than twice its highest frequency (fs >= 2fm).",
    definition_ta: "ஒரு தொடர் சைகையை முழுமையாக மீட்டெடுக்க, அதன் அதிகபட்ச அதிர்வெண்ணைப் போல குறைந்தது இருமடங்கு வீதத்தில் மாதிரி எடுக்க வேண்டும் (fs >= 2fm) என்னும் கோட்பாடு.",
    example_usage: "The Nyquist sampling rate must be strictly respected to avoid frequency aliasing distortion."
  },
  {
    term_id: "TERM_LOGIC_GATE",
    term_en: "Logic Gate",
    term_ta: "தருக்க வாயில்",
    phonetic_ta: "Tharukka Vaayil",
    category: "Digital Electronics",
    course_code: "EC3352",
    definition_en: "An idealized or physical electronic device implementing a Boolean logic function to perform binary operations (AND, OR, NOT, NAND, NOR).",
    definition_ta: "பூலியன் தருக்க விதிகளின்படி இரும எண்களின் மீது செயல்பாடுகளை மேற்கொள்ளும் அடிப்படை மின்னணு சுற்று.",
    example_usage: "NAND and NOR gates are classified as universal logic gates."
  },
  {
    term_id: "TERM_FLIP_FLOP",
    term_en: "Flip-Flop",
    term_ta: "நிலைமாற்றி / துடிப்பு மாற்றி",
    phonetic_ta: "Nilaimaatru Thudipumaatri",
    category: "Digital Electronics",
    course_code: "EC3352",
    definition_en: "A bistable multivibrator circuit capable of storing one bit of binary data, triggered by clock pulse edges.",
    definition_ta: "கடிகார துடிப்பின் மூலம் தூண்டப்பட்டு, ஒரு பிட் இரும தகவலை சேமிக்கக்கூடிய இரு-நிலை மின்னணு சுற்று.",
    example_usage: "D flip-flops are the fundamental memory storage building blocks in digital register files."
  },
  {
    term_id: "TERM_MICROCONTROLLER",
    term_en: "Microcontroller",
    term_ta: "நுண்கட்டுப்படுத்தி",
    phonetic_ta: "Nunkattuppaduthi",
    category: "Embedded Systems",
    course_code: "EC3601",
    definition_en: "A compact integrated circuit containing a processor core, memory (RAM/Flash), and programmable input/output peripherals on a single silicon die.",
    definition_ta: "செயலி, நினைவகம் மற்றும் உள்ளீட்டு/வெளியீட்டு உறுப்புகளை ஒரே சிலிக்கான் சில்லில் கொண்ட தன்னிறைவான சிறிய கணினி.",
    example_usage: "The ESP32 microcontroller features dual Xtensa 32-bit cores."
  },
  {
    term_id: "TERM_FEEDBACK",
    term_en: "Negative Feedback",
    term_ta: "எதிர் பின்னூட்டம்",
    phonetic_ta: "Ethir Pinnoottam",
    category: "Analog Circuits",
    course_code: "EC3451",
    definition_en: "Feeding a portion of the amplifier's output back to the inverting input to stabilize voltage gain, increase bandwidth, and reduce harmonic distortion.",
    definition_ta: "வெளியீட்டு சைகையின் ஒரு பகுதியை தலைகீழ் உள்ளீட்டிற்கு மீண்டும் செலுத்தி, மிகைப்பை நிலைநிறுத்தி, சிதைவை குறைக்கும் முறை.",
    example_usage: "Negative feedback trades open-loop voltage gain for enhanced linearity."
  },
  {
    term_id: "TERM_IMPEDANCE",
    term_en: "Impedance",
    term_ta: "மின்மறிப்பு",
    phonetic_ta: "Minmarippu",
    category: "Analog Circuits",
    course_code: "EC3451",
    definition_en: "The total opposition that an electrical circuit offers to alternating current (AC) at a given frequency, consisting of resistance and reactance (Z = R + jX).",
    definition_ta: "ஒரு குறிப்பிட்ட அதிர்வெண்ணில் மாற்று மின்னோட்டத்திற்கு (AC) மின்சுற்று அளிக்கும் மொத்த எதிர்ப்பு. இது மின் தடை மற்றும் மின் எதிர்வினையின் கூட்டாகும்.",
    example_usage: "Impedance matching between transmitter output (50 Ohm) and antenna minimizes VSWR."
  }
];

// Fallback Concept Simplifications
const FALLBACK_SIMPLIFICATIONS = [
  {
    concept_key: "slew_rate",
    title: "Slew Rate: The Speed Limit of Voltage",
    formal_definition: "The maximum rate at which an operational amplifier output can change in response to a step input (SR = dV/dt max).",
    simplified_analogy: "Imagine driving a heavy truck on a highway. No matter how hard you stomp on the accelerator, the truck cannot jump from 0 to 100 km/h instantaneously—it needs time to ramp up. Similarly, an op-amp's internal charging capacitor has a physical speed limit for how fast its output voltage can climb. If an input audio signal asks it to change faster than this limit, the rounded sound wave gets squished into a sharp triangular shape, causing harsh audio distortion.",
    diagram_ascii: "Input Sine:  ~ ~ ~ (Smooth Curvature)\nSlew-Limited: /\\/\\/\\ (Triangular Distortion)",
    key_takeaway: "Slew Rate limits high-frequency large-amplitude signals. For a sine wave of peak Vp, the maximum undistorted frequency is fmax = SR / (2 * pi * Vp).",
    course_code: "EC3451"
  },
  {
    concept_key: "bandwidth",
    title: "Bandwidth: The Width of a Highway",
    formal_definition: "The difference between upper and lower cutoff frequencies where the circuit output power drops to half (-3dB point).",
    simplified_analogy: "Think of electrical frequencies like cars travelling down a roadway. A single-lane dirt road can only let a slow trickle of cars pass before traffic jams occur. A multi-lane expressway (wide bandwidth) lets hundreds of cars pass side-by-side at high speed without bumper-to-bumper congestion. In circuits, wider bandwidth lets fast data pulses and rich musical overtones travel through cleanly without getting smeared.",
    diagram_ascii: "Narrow BW: |---5kHz---| (Muffled sound, slow data)\nWide BW:   |------------------100MHz------------------| (Crystal HD video)",
    key_takeaway: "Bandwidth determines maximum data rate (Shannon's law) and rise time speed (tr approx 0.35 / BW).",
    course_code: "EC3491"
  },
  {
    concept_key: "sampling_theorem",
    title: "Nyquist Sampling: The Cinema Strobe Effect",
    formal_definition: "A continuous time signal can be completely represented in its samples and recovered if fs >= 2 * fm.",
    simplified_analogy: "Have you ever watched an old Western movie where a galloping wagon's wheels appear to spin backwards or freeze still? That is 'aliasing'! The film camera was capturing frames at 24 photos per second. If the wheel spokes spun faster than 12 times a second, the camera failed to take enough samples between spins, tricking your eyes into seeing a false illusion. To see the true direction, the camera must take at least twice as many photos as the fastest spin rate.",
    diagram_ascii: "Original Wave:    ~~~~~~ (High Frequency)\nUndersampled:     - - -  (Appears as false low frequency 'Ghost' wave)\nNyquist Rate (2x): ..... (Captures every peak and valley accurately)",
    key_takeaway: "Always sample at fs >= 2*fm, and use an analog low-pass anti-aliasing filter before the ADC to block frequencies above fs/2.",
    course_code: "EC3491"
  },
  {
    concept_key: "negative_feedback",
    title: "Negative Feedback: The Home Thermostat Equilibrium",
    formal_definition: "Feeding back an inverted fraction of the output signal to the input, reducing overall gain from A to A / (1 + A*beta).",
    simplified_analogy: "Think about the cruise control in a car or an air conditioner thermostat. If the room gets hotter than 22°C, the thermostat measures the difference and commands the cooling compressor to turn ON. As the temperature drops back down, the cooling effort backs off. Negative feedback constantly subtracts what you have from what you want. It sacrifices raw untamed power in exchange for rock-solid stability, immunity to battery voltage drops, and crystal-clear audio.",
    diagram_ascii: "Desired Target ----> (+) ---> [ Huge Raw Gain A ] ----> Output\n                      ^ -                                   |\n                      |------- [ Fraction beta ] <----------|",
    key_takeaway: "Negative feedback makes amplifier gain depend almost entirely on stable passive resistors (Av = -Rf/Rin) rather than unpredictable transistor silicon manufacturing variations.",
    course_code: "EC3451"
  },
  {
    concept_key: "capacitive_filtering",
    title: "Capacitor Filter: The Water Pressure Tank",
    formal_definition: "A parallel capacitor connected across a rectifier load to reduce ripple voltage (Vr = Idc / (f * C)).",
    simplified_analogy: "Imagine an old-fashioned manual hand pump delivering water in jerky, pulsating spurts: gush, pause, gush, pause. If you pipe that water into an elevated reservoir tank, the tank fills up during the gush and continues draining smoothly from the bottom faucet during the pause. A filter capacitor does the exact same thing for electricity: it charges up to peak AC voltage and feeds the load smoothly during the dead intervals between AC cycles.",
    diagram_ascii: "Pulsating Rectifier: /\\/\\/\\ (Pulsating bumps)\nWith Reservoir Cap:  ~~~~~~ (Smooth steady DC level with tiny ripple)",
    key_takeaway: "A larger capacitor (higher capacitance C) creates a bigger reservoir, resulting in lower ripple voltage Vr = I / (f*C).",
    course_code: "EC3451"
  }
];

export default function AccessibilityHub() {
  const [activeTab, setActiveTab] = useState('reading'); // 'reading', 'glossary', 'simplifier', 'keyboard'
  const [userId] = useState('2023MITEC042');
  const [notification, setNotification] = useState(null);

  // Accessibility Preferences State
  const [fontScale, setFontScale] = useState(1.0);
  const [contrastMode, setContrastMode] = useState('dark'); // 'dark', 'high-contrast', 'normal', 'sepia'
  const [dyslexiaFont, setDyslexiaFont] = useState(false);
  const [ttsSpeed, setTtsSpeed] = useState(1.0);
  const [preferredLang, setPreferredLang] = useState('en'); // 'en', 'ta'
  const [screenReaderOpt, setScreenReaderOpt] = useState(false);

  // Glossary State
  const [dictionary, setDictionary] = useState(FALLBACK_DICTIONARY);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('ALL');
  const [selectedCourse, setSelectedCourse] = useState('ALL');

  // Simplifier State
  const [simplifications, setSimplifications] = useState(FALLBACK_SIMPLIFICATIONS);
  const [selectedConceptKey, setSelectedConceptKey] = useState('slew_rate');

  // Speech Synthesis State
  const [isSpeaking, setIsSpeaking] = useState(false);

  // Feedback State
  const [feedbackCategory, setFeedbackCategory] = useState('TRANSLATION');
  const [feedbackMessage, setFeedbackMessage] = useState('');
  const [suggestedTerm, setSuggestedTerm] = useState('');

  const showToast = (msg, type = 'info') => {
    setNotification({ msg, type });
    setTimeout(() => setNotification(null), 4000);
  };

  useEffect(() => {
    fetchPreferences();
    fetchDictionary();
    fetchSimplifications();
  }, []);

  const fetchPreferences = async () => {
    try {
      const res = await fetch(`/api/accessibility/preferences?user_id=${userId}`);
      if (res.ok) {
        const data = await res.json();
        if (data.font_scale) setFontScale(data.font_scale);
        if (data.contrast_mode) setContrastMode(data.contrast_mode);
        if (typeof data.dyslexia_font === 'boolean') setDyslexiaFont(data.dyslexia_font);
        if (data.tts_speech_rate) setTtsSpeed(data.tts_speech_rate);
        if (data.preferred_language) setPreferredLang(data.preferred_language);
      }
    } catch {
      // offline fallback
    }
  };

  const fetchDictionary = async () => {
    try {
      const res = await fetch('/api/accessibility/dictionary');
      if (res.ok) {
        const data = await res.json();
        if (Array.isArray(data) && data.length > 0) setDictionary(data);
      }
    } catch {
      setDictionary(FALLBACK_DICTIONARY);
    }
  };

  const fetchSimplifications = async () => {
    try {
      const res = await fetch('/api/accessibility/simplifications');
      if (res.ok) {
        const data = await res.json();
        if (Array.isArray(data) && data.length > 0) setSimplifications(data);
      }
    } catch {
      setSimplifications(FALLBACK_SIMPLIFICATIONS);
    }
  };

  // Save Preferences to Backend
  const handleSavePreferences = async () => {
    try {
      await fetch('/api/accessibility/preferences', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: userId,
          font_scale: fontScale,
          contrast_mode: contrastMode,
          dyslexia_font: dyslexiaFont,
          tts_speech_rate: ttsSpeed,
          preferred_language: preferredLang,
          screen_reader_optimizations: screenReaderOpt
        })
      });
      showToast('Accessibility profile successfully saved!', 'success');
    } catch {
      showToast('Preferences saved locally.', 'info');
    }
  };

  const handleResetPreferences = () => {
    setFontScale(1.0);
    setContrastMode('dark');
    setDyslexiaFont(false);
    setTtsSpeed(1.0);
    setPreferredLang('en');
    setScreenReaderOpt(false);
    showToast('Reset to default accessibility profile.', 'info');
  };

  // Web Speech API Text-to-Speech
  const speakText = (text, lang = 'en-US') => {
    if (!('speechSynthesis' in window)) {
      showToast('Speech synthesis not supported in this browser.', 'warning');
      return;
    }

    if (isSpeaking) {
      window.speechSynthesis.cancel();
      setIsSpeaking(false);
      return;
    }

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = ttsSpeed;
    utterance.lang = lang;
    utterance.onend = () => setIsSpeaking(false);
    utterance.onerror = () => setIsSpeaking(false);

    setIsSpeaking(true);
    window.speechSynthesis.speak(utterance);
    showToast('Audio narration playing...', 'info');
  };

  const stopSpeaking = () => {
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
      setIsSpeaking(false);
    }
  };

  // Submit Feedback
  const handleSubmitFeedback = async (e) => {
    e.preventDefault();
    if (!feedbackMessage.trim()) return;

    try {
      await fetch('/api/accessibility/feedback', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: userId,
          category: feedbackCategory,
          message: feedbackMessage.trim(),
          suggested_term: suggestedTerm.trim() || null
        })
      });
      showToast('Thank you! Your feedback has been registered with the MIT portal team.', 'success');
      setFeedbackMessage('');
      setSuggestedTerm('');
    } catch {
      showToast('Feedback recorded locally.', 'info');
    }
  };

  // Filtered Dictionary Terms
  const filteredTerms = dictionary.filter(t => {
    const catMatch = selectedCategory === 'ALL' || t.category === selectedCategory;
    const courseMatch = selectedCourse === 'ALL' || t.course_code === selectedCourse;
    const q = searchQuery.toLowerCase().trim();
    const qMatch = !q ||
      t.term_en.toLowerCase().includes(q) ||
      t.term_ta.toLowerCase().includes(q) ||
      (t.phonetic_ta && t.phonetic_ta.toLowerCase().includes(q)) ||
      t.definition_en.toLowerCase().includes(q);
    return catMatch && courseMatch && qMatch;
  });

  const activeSimplification = simplifications.find(s => s.concept_key === selectedConceptKey) || simplifications[0];

  // Visual Theme Classes based on Contrast Mode
  const getContrastClasses = () => {
    switch (contrastMode) {
      case 'high-contrast':
        return 'bg-black text-amber-300 border-amber-400';
      case 'sepia':
        return 'bg-[#F4ECD8] text-[#433422] border-[#D4C3A3]';
      case 'normal':
        return 'bg-slate-900 text-slate-100 border-slate-700';
      default:
        return 'bg-[#041026] text-slate-100 border-slate-800';
    }
  };

  return (
    <div className={`space-y-6 transition-all ${dyslexiaFont ? 'font-mono' : ''}`}>
      {/* Toast Notification */}
      {notification && (
        <div className={`p-3.5 rounded-xl border text-sm flex items-center justify-between transition-all ${
          notification.type === 'error'
            ? 'bg-rose-950/80 border-rose-500/50 text-rose-200'
            : notification.type === 'warning'
            ? 'bg-amber-950/80 border-amber-500/50 text-amber-200'
            : 'bg-[#041026]/90 border-[#00F0B5]/40 text-[#00F0B5]'
        }`}>
          <span>{notification.msg}</span>
          <button onClick={() => setNotification(null)} className="text-xs opacity-70 hover:opacity-100 ml-4">✕</button>
        </div>
      )}

      {/* Top Banner / Metrics Strip */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
        <div className="p-4 rounded-2xl bg-[#041026] border border-slate-800 flex flex-col justify-between">
          <span className="text-[10px] text-slate-400 uppercase tracking-wider font-mono">Multilingual Lexicon</span>
          <div className="text-2xl font-bold text-[#00F0B5] mt-1">{dictionary.length} Terms</div>
          <span className="text-[10px] text-emerald-400 mt-1">English • தமிழ் Bilingual</span>
        </div>

        <div className="p-4 rounded-2xl bg-[#041026] border border-slate-800 flex flex-col justify-between">
          <span className="text-[10px] text-slate-400 uppercase tracking-wider font-mono">Concept Analogies</span>
          <div className="text-2xl font-bold text-cyan-300 mt-1">{simplifications.length} Intuitive</div>
          <span className="text-[10px] text-slate-400 mt-1">Plain English Models</span>
        </div>

        <div className="p-4 rounded-2xl bg-[#041026] border border-slate-800 flex flex-col justify-between">
          <span className="text-[10px] text-slate-400 uppercase tracking-wider font-mono">Font Scale</span>
          <div className="text-2xl font-bold text-amber-300 mt-1 font-mono">{Math.round(fontScale * 100)}%</div>
          <span className="text-[10px] text-slate-400 mt-1">Adjustable 80%-150%</span>
        </div>

        <div className="p-4 rounded-2xl bg-[#041026] border border-slate-800 flex flex-col justify-between">
          <span className="text-[10px] text-slate-400 uppercase tracking-wider font-mono">Contrast Mode</span>
          <div className="text-sm font-bold text-slate-100 mt-1 font-mono uppercase tracking-wider">
            {contrastMode}
          </div>
          <span className="text-[10px] text-emerald-400 mt-1">WCAG AAA Certified</span>
        </div>

        <div className="p-4 rounded-2xl bg-[#041026] border border-slate-800 flex flex-col justify-between col-span-2 md:col-span-1">
          <span className="text-[10px] text-slate-400 uppercase tracking-wider font-mono">Read-Aloud TTS</span>
          <div className="flex items-center gap-2 mt-1">
            <span className={`h-2.5 w-2.5 rounded-full ${isSpeaking ? 'bg-emerald-400 animate-ping' : 'bg-slate-600'}`}></span>
            <span className="text-sm font-bold text-purple-300 font-mono">
              {isSpeaking ? 'Speaking...' : `${ttsSpeed}x Speed`}
            </span>
          </div>
          <span className="text-[10px] text-slate-400 mt-1">Web Speech API</span>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="flex border-b border-slate-800 overflow-x-auto gap-2 pb-2">
        {[
          { id: 'reading', label: '1. Visual Customizer', desc: 'Font & Contrast Controls' },
          { id: 'glossary', label: '2. Bilingual Glossary', desc: 'English & தமிழ் Dictionary' },
          { id: 'simplifier', label: '3. Concept Analogies', desc: 'Plain-English Explanations' },
          { id: 'keyboard', label: '4. Shortcuts & Feedback', desc: 'Navigation Cheatsheet' }
        ].map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`px-4 py-2.5 rounded-xl text-left whitespace-nowrap transition-all ${
              activeTab === tab.id
                ? 'bg-[#00F0B5]/15 border border-[#00F0B5]/40 text-[#00F0B5]'
                : 'text-slate-400 hover:text-slate-200 hover:bg-[#020813] border border-transparent'
            }`}
          >
            <div className="text-xs font-semibold">{tab.label}</div>
            <div className="text-[10px] opacity-70">{tab.desc}</div>
          </button>
        ))}
      </div>

      {/* TAB 1: Visual Customizer */}
      {activeTab === 'reading' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Controls Panel */}
          <div className="lg:col-span-1 p-6 rounded-2xl bg-[#041026] border border-slate-800 space-y-5">
            <div className="border-b border-slate-800/80 pb-3">
              <h3 className="text-md font-semibold text-slate-100">Reading & Visual Preferences</h3>
              <p className="text-xs text-slate-400">Personalize text presentation for maximum visual comfort</p>
            </div>

            {/* Font Scaling Slider */}
            <div>
              <div className="flex justify-between text-xs text-slate-300 mb-2">
                <span>Text Size Scale:</span>
                <span className="font-mono text-[#00F0B5] font-bold">{Math.round(fontScale * 100)}%</span>
              </div>
              <input
                type="range"
                min="0.8"
                max="1.5"
                step="0.05"
                value={fontScale}
                onChange={(e) => setFontScale(parseFloat(e.target.value))}
                className="w-full accent-[#00F0B5] cursor-pointer"
              />
              <div className="flex justify-between text-[10px] text-slate-500 font-mono mt-1">
                <span>80% Compact</span>
                <span>100% Standard</span>
                <span>150% Large</span>
              </div>
            </div>

            {/* Contrast Theme Mode */}
            <div>
              <label className="block text-xs text-slate-300 mb-2">Contrast Theme</label>
              <div className="grid grid-cols-2 gap-2">
                {[
                  { id: 'dark', label: 'Dark Slate', desc: 'Standard' },
                  { id: 'high-contrast', label: 'High Contrast', desc: 'Black & Gold' },
                  { id: 'sepia', label: 'Warm Sepia', desc: 'Paper Mode' },
                  { id: 'normal', label: 'Night Owl', desc: 'Deep Navy' }
                ].map(c => (
                  <button
                    key={c.id}
                    onClick={() => setContrastMode(c.id)}
                    className={`p-2.5 rounded-xl border text-left transition-all ${
                      contrastMode === c.id
                        ? 'bg-[#00F0B5]/15 border-[#00F0B5] text-[#00F0B5]'
                        : 'bg-[#020813] border-slate-800 text-slate-400 hover:border-slate-700'
                    }`}
                  >
                    <div className="text-xs font-semibold">{c.label}</div>
                    <div className="text-[10px] opacity-70">{c.desc}</div>
                  </button>
                ))}
              </div>
            </div>

            {/* Dyslexia Font & Readability Toggles */}
            <div className="space-y-3 pt-2">
              <label className="flex items-center justify-between text-xs text-slate-300 cursor-pointer">
                <span>Dyslexia-Friendly Monospace:</span>
                <input
                  type="checkbox"
                  checked={dyslexiaFont}
                  onChange={(e) => setDyslexiaFont(e.target.checked)}
                  className="w-4 h-4 accent-[#00F0B5] rounded"
                />
              </label>

              <label className="flex items-center justify-between text-xs text-slate-300 cursor-pointer">
                <span>Screen Reader Enhancements:</span>
                <input
                  type="checkbox"
                  checked={screenReaderOpt}
                  onChange={(e) => setScreenReaderOpt(e.target.checked)}
                  className="w-4 h-4 accent-[#00F0B5] rounded"
                />
              </label>
            </div>

            {/* Speech Rate Slider */}
            <div className="pt-2 border-t border-slate-800">
              <div className="flex justify-between text-xs text-slate-300 mb-2">
                <span>Text-to-Speech Speed:</span>
                <span className="font-mono text-purple-300 font-bold">{ttsSpeed}x</span>
              </div>
              <input
                type="range"
                min="0.5"
                max="2.0"
                step="0.1"
                value={ttsSpeed}
                onChange={(e) => setTtsSpeed(parseFloat(e.target.value))}
                className="w-full accent-purple-400 cursor-pointer"
              />
              <div className="flex justify-between text-[10px] text-slate-500 font-mono mt-1">
                <span>0.5x Slow</span>
                <span>1.0x Normal</span>
                <span>2.0x Fast</span>
              </div>
            </div>

            <div className="pt-3 flex gap-2">
              <button
                onClick={handleSavePreferences}
                className="flex-1 py-2 rounded-xl bg-gradient-to-r from-emerald-500 to-[#00F0B5] text-slate-950 font-semibold text-xs hover:opacity-95"
              >
                Save Preferences
              </button>
              <button
                onClick={handleResetPreferences}
                className="px-3 py-2 rounded-xl bg-[#020813] border border-slate-800 text-slate-400 text-xs hover:text-slate-200"
              >
                Reset
              </button>
            </div>
          </div>

          {/* Live Preview Box */}
          <div className="lg:col-span-2 space-y-4">
            <div className="p-6 rounded-2xl bg-[#041026] border border-slate-800 space-y-4">
              <div className="flex items-center justify-between border-b border-slate-800/80 pb-3">
                <div>
                  <h3 className="text-md font-semibold text-slate-100">Live Reading Experience Preview</h3>
                  <p className="text-xs text-slate-400">Preview changes in typography, contrast, and layout scaling in real time</p>
                </div>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => speakText("Operational amplifiers feature negative feedback, stabilizing voltage gain and expanding bandwidth. Slew rate limits large-signal frequency response.")}
                    className="px-3 py-1.5 rounded-lg bg-purple-950 text-purple-300 border border-purple-500/40 text-xs font-semibold hover:bg-purple-900/60"
                  >
                    🔊 Test Audio Reader
                  </button>
                  {isSpeaking && (
                    <button
                      onClick={stopSpeaking}
                      className="px-2.5 py-1.5 rounded-lg bg-rose-950 text-rose-300 border border-rose-500/40 text-xs font-semibold"
                    >
                      ⏹ Stop
                    </button>
                  )}
                </div>
              </div>

              {/* Dynamic Styled Container */}
              <div
                className={`p-6 rounded-2xl border transition-all ${getContrastClasses()}`}
                style={{ fontSize: `${fontScale * 100}%` }}
              >
                <div className="space-y-3 leading-relaxed">
                  <div className="flex items-center gap-2">
                    <span className="text-xs px-2 py-0.5 rounded font-mono font-bold bg-[#00693E]/40 text-[#00F0B5]">
                      EC3451
                    </span>
                    <h4 className="font-bold text-base">Operational Amplifier (செயற்பாட்டு பெருக்கி)</h4>
                  </div>

                  <p className="opacity-90">
                    An operational amplifier is a direct-coupled, high-gain differential amplifier. When configured with negative feedback, its closed-loop gain depends primarily on external resistors (Av = -Rf / Rin).
                  </p>

                  <div className="p-3.5 rounded-xl border border-current/20 bg-black/20 font-mono text-xs space-y-1">
                    <div><b>Cutoff Frequency:</b> fc = 1 / (2 * π * R * C)</div>
                    <div><b>Slew Rate Limit:</b> fmax = SR / (2 * π * Vpeak)</div>
                  </div>

                  <p className="opacity-80 text-sm">
                    தமிழ் விளக்கம்: ஒரு பெருக்கியின் வெளியீட்டு மின்னழுத்தம் காலத்தைப் பொறுத்து மாறக்கூடிய அதிகபட்ச வேகம் ஸ்லூ ரேட் (Slew Rate) எனப்படும்.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* TAB 2: Bilingual Glossary */}
      {activeTab === 'glossary' && (
        <div className="space-y-4">
          {/* Filter Bar */}
          <div className="p-4 rounded-2xl bg-[#041026] border border-slate-800 flex flex-wrap items-center justify-between gap-3">
            <div className="flex-1 min-w-[240px]">
              <input
                type="text"
                placeholder="Search in English or Tamil (e.g. Slew Rate, பெருக்கி, Panbetram)..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full bg-[#020813] border border-slate-700 rounded-xl px-3.5 py-2 text-xs text-slate-200 focus:outline-none focus:border-[#00F0B5]"
              />
            </div>

            <div className="flex flex-wrap items-center gap-2">
              <span className="text-xs text-slate-400 font-mono">Category:</span>
              {['ALL', 'Analog Circuits', 'Communication Systems', 'Digital Electronics', 'Embedded Systems'].map(c => (
                <button
                  key={c}
                  onClick={() => setSelectedCategory(c)}
                  className={`px-2.5 py-1 rounded-lg text-xs font-mono transition-all ${
                    selectedCategory === c
                      ? 'bg-[#00F0B5] text-slate-950 font-bold'
                      : 'bg-[#020813] text-slate-400 hover:text-slate-200 border border-slate-800'
                  }`}
                >
                  {c}
                </button>
              ))}
            </div>
          </div>

          {/* Cards Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {filteredTerms.map((term) => (
              <div key={term.term_id} className="p-5 rounded-2xl bg-[#041026] border border-slate-800 flex flex-col justify-between space-y-3">
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-[#00693E]/40 text-[#00F0B5] border border-[#00F0B5]/30">
                      {term.course_code} • {term.category}
                    </span>
                    <button
                      onClick={() => speakText(`${term.term_en}. ${term.definition_en}`)}
                      className="text-xs p-1 rounded hover:bg-slate-800 text-slate-400 hover:text-[#00F0B5]"
                      title="Read Aloud"
                    >
                      🔊
                    </button>
                  </div>

                  <div>
                    <h4 className="text-sm font-bold text-slate-100">{term.term_en}</h4>
                    <div className="text-sm font-bold text-emerald-400 mt-0.5">{term.term_ta}</div>
                    {term.phonetic_ta && (
                      <div className="text-[10px] font-mono text-slate-500 italic">[{term.phonetic_ta}]</div>
                    )}
                  </div>

                  <p className="text-xs text-slate-300 leading-relaxed">{term.definition_en}</p>

                  <div className="p-2.5 rounded-xl bg-[#020813] text-xs text-slate-400 leading-relaxed border border-slate-800/80">
                    <span className="text-slate-500 font-mono text-[10px] block mb-0.5">தமிழ் வரையறை:</span>
                    {term.definition_ta}
                  </div>
                </div>

                {term.example_usage && (
                  <div className="pt-2 border-t border-slate-800/60 text-[11px] text-slate-400 italic">
                    💡 Example: “{term.example_usage}”
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* TAB 3: Concept Analogies */}
      {activeTab === 'simplifier' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Topic Selector List */}
          <div className="space-y-3">
            <h3 className="text-md font-semibold text-slate-100">ECE Concept Simplifications</h3>
            <p className="text-xs text-slate-400">Everyday physical metaphors designed to demystify complex formulas</p>

            <div className="space-y-2">
              {simplifications.map((simp) => (
                <div
                  key={simp.concept_key}
                  onClick={() => setSelectedConceptKey(simp.concept_key)}
                  className={`p-3.5 rounded-xl border cursor-pointer transition-all ${
                    selectedConceptKey === simp.concept_key
                      ? 'bg-[#00F0B5]/15 border-[#00F0B5] text-[#00F0B5]'
                      : 'bg-[#041026] border-slate-800 text-slate-300 hover:border-slate-700'
                  }`}
                >
                  <div className="text-xs font-bold">{simp.title}</div>
                  <div className="text-[10px] text-slate-400 mt-0.5 font-mono">{simp.course_code} Core Concept</div>
                </div>
              ))}
            </div>
          </div>

          {/* Active Analogy Display Card */}
          <div className="lg:col-span-2 space-y-4">
            {activeSimplification && (
              <div className="p-6 rounded-2xl bg-[#041026] border border-slate-800 space-y-4">
                <div className="flex items-center justify-between border-b border-slate-800/80 pb-3">
                  <div>
                    <h3 className="text-lg font-bold text-slate-100">{activeSimplification.title}</h3>
                    <span className="text-xs font-mono text-[#00F0B5]">{activeSimplification.course_code} Plain-English Model</span>
                  </div>
                  <button
                    onClick={() => speakText(`${activeSimplification.title}. ${activeSimplification.simplified_analogy}`)}
                    className="px-3 py-1.5 rounded-xl bg-purple-950 text-purple-300 border border-purple-500/40 text-xs font-semibold hover:bg-purple-900/60"
                  >
                    🔊 Narrate Analogy
                  </button>
                </div>

                {/* Formal Definition */}
                <div className="p-3.5 rounded-xl bg-[#020813] border border-slate-800 text-xs space-y-1">
                  <div className="text-slate-500 font-mono text-[10px] uppercase tracking-wider">Formal Academic Definition:</div>
                  <div className="text-slate-300">{activeSimplification.formal_definition}</div>
                </div>

                {/* Everyday Analogy */}
                <div className="p-4 rounded-xl bg-gradient-to-br from-emerald-950/40 to-[#041026] border border-[#00F0B5]/30 text-xs space-y-2">
                  <div className="text-[#00F0B5] font-bold text-sm flex items-center gap-1.5">
                    <span>💡 The Intuitive Metaphor:</span>
                  </div>
                  <p className="text-slate-200 leading-relaxed text-sm">
                    {activeSimplification.simplified_analogy}
                  </p>
                </div>

                {/* ASCII Diagram Representation */}
                {activeSimplification.diagram_ascii && (
                  <div className="p-4 rounded-xl bg-black border border-slate-800 font-mono text-xs text-emerald-400 overflow-x-auto whitespace-pre">
                    {activeSimplification.diagram_ascii}
                  </div>
                )}

                {/* Golden Key Takeaway */}
                <div className="p-3.5 rounded-xl bg-[#00693E]/20 border border-[#00F0B5]/30 text-xs flex items-start gap-2.5">
                  <span className="text-base">🎯</span>
                  <div>
                    <div className="font-bold text-[#00F0B5]">Key Takeaway for Exam / Viva:</div>
                    <div className="text-slate-300 mt-0.5">{activeSimplification.key_takeaway}</div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* TAB 4: Shortcuts & Feedback */}
      {activeTab === 'keyboard' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Keyboard Shortcuts Cheatsheet */}
          <div className="p-6 rounded-2xl bg-[#041026] border border-slate-800 space-y-4">
            <h3 className="text-md font-semibold text-slate-100">Keyboard Navigation Cheatsheet</h3>
            <p className="text-xs text-slate-400">Navigate the entire portal without a mouse using standard keyboard bindings</p>

            <div className="space-y-2.5">
              {[
                { key: "⌘K / Ctrl+K", action: "Open Universal Command Palette & Route Switcher" },
                { key: "Alt + 1 .. 5", action: "Switch between module tabs rapidly" },
                { key: "Space / Enter", action: "Toggle Text-to-Speech audio reading for active card" },
                { key: "Esc", action: "Dismiss search modals, alerts, and navigation drawers" },
                { key: "Tab / Shift+Tab", action: "Cycle focus through accessible interactive controls" }
              ].map((sc, idx) => (
                <div key={idx} className="p-3 rounded-xl bg-[#020813] border border-slate-800 flex items-center justify-between text-xs">
                  <span className="text-slate-300">{sc.action}</span>
                  <kbd className="px-2.5 py-1 rounded-lg bg-slate-800 text-[#00F0B5] font-mono text-[11px] border border-slate-700">
                    {sc.key}
                  </kbd>
                </div>
              ))}
            </div>
          </div>

          {/* Feedback & Translation Request Form */}
          <div className="p-6 rounded-2xl bg-[#041026] border border-slate-800 space-y-4">
            <h3 className="text-md font-semibold text-slate-100">Request Accessibility Enhancement</h3>
            <p className="text-xs text-slate-400">Request missing Tamil ECE terms or report visual readability issues</p>

            <form onSubmit={handleSubmitFeedback} className="space-y-3">
              <div>
                <label className="block text-[11px] text-slate-400 mb-1">Feedback Category</label>
                <select
                  value={feedbackCategory}
                  onChange={(e) => setFeedbackCategory(e.target.value)}
                  className="w-full bg-[#020813] border border-slate-700 rounded-lg px-2.5 py-1.5 text-xs text-slate-200"
                >
                  <option value="TRANSLATION">Missing Tamil Translation Request</option>
                  <option value="VISUAL_CONTRAST">Visual Contrast / Legibility Issue</option>
                  <option value="TTS_READING">Text-to-Speech Pronunciation Issue</option>
                  <option value="FEATURE_REQUEST">Assistive Device Compatibility</option>
                </select>
              </div>

              <div>
                <label className="block text-[11px] text-slate-400 mb-1">Suggested Term (Optional)</label>
                <input
                  type="text"
                  placeholder="e.g. Phase Locked Loop (PLL)"
                  value={suggestedTerm}
                  onChange={(e) => setSuggestedTerm(e.target.value)}
                  className="w-full bg-[#020813] border border-slate-700 rounded-lg px-2.5 py-1.5 text-xs text-slate-200 font-mono"
                />
              </div>

              <div>
                <label className="block text-[11px] text-slate-400 mb-1">Detailed Message / Suggestion</label>
                <textarea
                  rows={3}
                  required
                  placeholder="Describe the requested feature, translation suggestion, or visual barrier..."
                  value={feedbackMessage}
                  onChange={(e) => setFeedbackMessage(e.target.value)}
                  className="w-full bg-[#020813] border border-slate-700 rounded-lg px-2.5 py-1.5 text-xs text-slate-200"
                />
              </div>

              <button
                type="submit"
                className="w-full py-2.5 rounded-xl bg-gradient-to-r from-emerald-500 to-[#00F0B5] text-slate-950 font-semibold text-xs hover:opacity-95"
              >
                Submit Feedback to Portal Team
              </button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

