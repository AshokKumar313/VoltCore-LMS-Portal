import React, { useState } from 'react';

/**
 * ========================================================================================
 * VoltCore Apex Academia - Phase M: Collaboration & Community (Features 331–340)
 * Anna University / MIT Campus - Department of Electronics Engineering (Regulation 2023)
 * Platform Lead: Ashok Kumar A (2023MITEC042)
 *
 * Features:
 *   - Feature 331: Student Discussion Forums (ECE Topics, Threads, Upvoting, Solution Marking)
 *   - Feature 332: Subject-Wise Question Community (Anna Univ Reg 2023 Core Codes)
 *   - Feature 333: Study Group Creator (Virtual rooms, schedules, peer join/leave)
 *   - Feature 334: Collaborative Notes Workspace (Markdown notes, revision tags, export)
 *   - Feature 335: Peer Assignment Review (Rubric-based evaluation, weighted scoring)
 *   - Feature 336: Project Team Discussion Board (Channels, sprint tasks, status boards)
 *   - Feature 337: Faculty Doubt-Clearing Portal (Direct query to professors, priority queues)
 *   - Feature 338: Shared Resource Library (SPICE netlists, Verilog TB, MATLAB, notes)
 *   - Feature 339: Student Knowledge Contribution Points (Karma, badges, leaderboard)
 *   - Feature 340: Academic Announcement Feed (Anna University & MIT Campus circulars)
 * Hardware Safe: Zero background polling loops, SQLite WAL mode, passive CPU footprint.
 * ========================================================================================
 */

// Initial Seed Data for Forums (Feature 331 & 332)
const SEED_FORUM_POSTS = [
  {
    id: "post_01",
    title: "Resolving Hold Time Violations on TSMC 28nm Cell Library",
    category: "VLSI",
    subject_code: "EC3552",
    author_name: "Ashok Kumar A",
    author_roll: "2023MITEC042",
    content: "During post-CTS STA in Cadence Innovus, we are seeing -120ps hold slack on the fast-fast (0.9V, -40C) corner. What is the standard buffer insertion strategy to resolve hold without creating max capacitance violations?",
    tags: ["VLSI", "STA", "Innovus", "TimingClosure"],
    upvotes: 14,
    created_at: "2026-11-05T10:30:00Z",
    replies: [
      {
        id: "rep_01_1",
        author_name: "Kavitha R",
        author_roll: "2023MITEC055",
        content: "Hold time is independent of clock period. Insert low-drive delay cells (e.g. DEL_X1) near the capture flip-flop's D-pin. Avoid inserting at branch points to prevent branching load spikes.",
        upvotes: 9,
        is_solution: true
      }
    ]
  },
  {
    id: "post_02",
    title: "FreeRTOS Priority Inversion with Mutex vs Binary Semaphore",
    category: "Embedded",
    subject_code: "EC3711",
    author_name: "Dinesh S",
    author_roll: "2023MITEC010",
    content: "Why does using xSemaphoreCreateBinary() instead of xSemaphoreCreateMutex() cause unbound priority inversion when a medium-priority task preempts the low-priority resource holder?",
    tags: ["FreeRTOS", "RTOS", "EmbeddedC", "ARM"],
    upvotes: 11,
    created_at: "2026-11-04T16:15:00Z",
    replies: [
      {
        id: "rep_02_1",
        author_name: "Ashok Kumar A",
        author_roll: "2023MITEC042",
        content: "Binary semaphores lack Priority Inheritance. Mutexes in FreeRTOS temporarily elevate the priority of the holding task to match the highest-priority blocked task.",
        upvotes: 8,
        is_solution: true
      }
    ]
  },
  {
    id: "post_03",
    title: "Sallen-Key Active Filter Q-Factor Peaking in LTspice",
    category: "Analog",
    subject_code: "EC3451",
    author_name: "Swetha M",
    author_roll: "2023MITEC018",
    content: "When designing an equal-component Sallen-Key low pass filter with fc=10kHz, my passband exhibits a 4dB resonant peak. Which capacitor ratio dampens the quality factor Q to 0.707 (Butterworth)?",
    tags: ["Analog", "LTspice", "Filters", "OpAmp"],
    upvotes: 7,
    created_at: "2026-11-03T11:00:00Z",
    replies: []
  }
];

// Anna University Reg 2023 ECE Subjects (Feature 332)
const REG2023_SUBJECTS = [
  { code: "EC3351", name: "Control Systems", sem: 3 },
  { code: "EC3352", name: "Digital Systems Design", sem: 3 },
  { code: "EC3451", name: "Linear Integrated Circuits", sem: 4 },
  { code: "EC3452", name: "Electromagnetic Fields", sem: 4 },
  { code: "EC3501", name: "Wireless Communication", sem: 5 },
  { code: "EC3551", name: "Transmission Lines and RF Systems", sem: 5 },
  { code: "EC3552", name: "VLSI and Chip Design", sem: 5 },
  { code: "EC3601", name: "Medical Electronics", sem: 6 }
];

// Seed Study Groups (Feature 333)
const SEED_STUDY_GROUPS = [
  {
    id: "sg_01",
    name: "VLSI RTL-to-GDSII Deep Dive Cohort",
    subject: "EC3552 (VLSI and Chip Design)",
    topic: "OpenROAD Synthesis, Global Routing & DRC/LVS Clean-up",
    max_members: 6,
    members: ["Ashok Kumar A (2023MITEC042)", "Kavitha R (2023MITEC055)", "Dinesh S (2023MITEC010)"],
    schedule: "Tuesdays & Thursdays • 18:30 – 20:00 IST",
    room_url: "https://meet.jit.si/voltcore-vlsi-openroad"
  },
  {
    id: "sg_02",
    name: "ARM Cortex-M4 FreeRTOS HIL Group",
    subject: "EC3711 (Embedded Systems Lab)",
    topic: "DMA Circular Buffers, FreeRTOS Queues & JTAG Trace",
    max_members: 5,
    members: ["Ashok Kumar A (2023MITEC042)", "Priya B (2023MITEC033)"],
    schedule: "Wednesdays • 17:00 – 19:00 IST",
    room_url: "https://meet.jit.si/voltcore-arm-rtos-hil"
  },
  {
    id: "sg_03",
    name: "Smith Chart & Microwave Matching Circle",
    subject: "EC3551 (Transmission Lines & RF)",
    topic: "Single & Double Stub Impedance Matching for 2.4GHz ISM",
    max_members: 4,
    members: ["Ramesh K (2023MITEC088)"],
    schedule: "Saturdays • 10:00 – 12:00 IST",
    room_url: "https://meet.jit.si/voltcore-rf-smith-chart"
  }
];

// Seed Collaborative Notes (Feature 334)
const SEED_NOTES = [
  {
    id: "note_01",
    title: "Static Timing Analysis: Setup & Hold Timing Closure",
    subject: "EC3552",
    version: 3,
    authors: ["Ashok Kumar A", "Kavitha R"],
    tags: ["STA", "Slack", "ClockSkew", "Jitter"],
    content: `# Static Timing Analysis (STA) Equation Sheet

## 1. Setup Time Check (Max Path / Slow Corner)
$$T_{clk} - t_{setup} - t_{skew} - t_{jitter} \\ge t_{cq} + t_{comb}$$
- Setup Slack: $WNS = \\min(T_{clk} - (t_{cq} + t_{comb} + t_{setup} + t_{skew}))$.
- If $WNS < 0$, downscale frequency or optimize datapath logic gates.

## 2. Hold Time Check (Min Path / Fast Corner)
$$t_{cq} + t_{comb} \\ge t_{hold} + t_{skew}$$
- Hold Slack is independent of $T_{clk}$!
- Violation fix: Add buffer delay cells in the datapath.`
  },
  {
    id: "note_02",
    title: "Maxwell's Equations & Boundary Conditions Summary",
    subject: "EC3452",
    version: 2,
    authors: ["Ashok Kumar A"],
    tags: ["EMF", "Maxwell", "Dielectrics"],
    content: `# Maxwell's Four Fundamental Equations

1. **Gauss's Law (Electrostatics)**: $\\nabla \\cdot \\mathbf{D} = \\rho_v$
2. **Gauss's Law for Magnetism**: $\\nabla \\cdot \\mathbf{B} = 0$
3. **Faraday's Law of Induction**: $\\nabla \\times \\mathbf{E} = -\\frac{\\partial \\mathbf{B}}{\\partial t}$
4. **Ampere-Maxwell Law**: $\\nabla \\times \\mathbf{H} = \\mathbf{J} + \\frac{\\partial \\mathbf{D}}{\\partial t}$`
  }
];

// Faculty Directory (Feature 337)
const FACULTY_LIST = [
  {
    id: "fac_01",
    name: "Dr. P. Nirmal",
    title: "Professor & Head",
    spec: "VLSI Architecture, Low Power ASIC Design",
    office: "Tues/Thurs 14:00 – 16:00 IST (Room ECE-302)"
  },
  {
    id: "fac_02",
    name: "Dr. S. Malarvizhi",
    title: "Associate Professor",
    spec: "Embedded Systems, RTOS, ARM Cortex-M Architecture",
    office: "Mon/Wed 10:00 – 12:00 IST (Room ECE-215)"
  },
  {
    id: "fac_03",
    name: "Dr. V. Sathiesh Kumar",
    title: "Assistant Professor (Sr. Gr.)",
    spec: "Wireless Comm, RF Circuits, Microstrip Antennas",
    office: "Fri 11:00 – 13:00 IST (Room ECE-108)"
  },
  {
    id: "fac_04",
    name: "Dr. T. S. Pradeep Kumar",
    title: "Associate Professor",
    spec: "IoT Networks, Edge TinyML, LoRaWAN Protocols",
    office: "Wed/Fri 14:30 – 16:30 IST (Room ECE-204)"
  }
];

// Seed Faculty Doubts (Feature 337)
const SEED_DOUBTS = [
  {
    id: "dbt_01",
    student_roll: "2023MITEC042",
    faculty_id: "fac_01",
    faculty_name: "Dr. P. Nirmal",
    subject_code: "EC3552",
    query: "Sir, when setting up On-Chip Variation (OCV) derating for 16nm FinFET, how should early and late derate factors be configured for hold vs setup checks?",
    priority: "HIGH",
    status: "RESOLVED",
    response: "For setup check: apply late derate (e.g. 1.05) to launch clock and data path, and early derate (0.95) to capture clock. For hold check: invert the derates to stress the min datapath."
  },
  {
    id: "dbt_02",
    student_roll: "2023MITEC010",
    faculty_id: "fac_02",
    faculty_name: "Dr. S. Malarvizhi",
    subject_code: "EC3711",
    query: "Ma'am, does FreeRTOS vApplicationStackOverflowHook require hardware MPU configuration, or does it rely solely on watermark checking?",
    priority: "MEDIUM",
    status: "RESOLVED",
    response: "Method 1 uses watermark fill checking at context switch. Method 2 checks the last 16 bytes of the stack. With Cortex-M MPU ports, hardware MPU provides synchronous fault isolation."
  }
];

// Shared Resources (Feature 338)
const SEED_RESOURCES = [
  {
    id: "res_01",
    title: "LTspice Simulation Deck: TSMC 65nm CMOS Inverter VTC & Noise Margins",
    category: "SPICE_NETLIST",
    subject: "EC3552",
    author: "Ashok Kumar A (2023MITEC042)",
    upvotes: 28,
    downloads: 142,
    url: "https://voltcore.annauniv.edu/repo/cmos_65nm_vtc.cir"
  },
  {
    id: "res_02",
    title: "SystemVerilog Testbench: AXI4-Lite Slave with Random Constrained Assertions",
    category: "VERILOG_TB",
    subject: "EC3352",
    author: "Kavitha R (2023MITEC055)",
    upvotes: 22,
    downloads: 98,
    url: "https://voltcore.annauniv.edu/repo/axi4_lite_slave_tb.sv"
  },
  {
    id: "res_03",
    title: "MATLAB Script: 16-QAM Constellation with Rayleigh Fading BER Curve",
    category: "MATLAB_SCRIPT",
    subject: "EC3501",
    author: "Dinesh S (2023MITEC010)",
    upvotes: 19,
    downloads: 87,
    url: "https://voltcore.annauniv.edu/repo/qam16_rayleigh_ber.m"
  },
  {
    id: "res_04",
    title: "Annotated Datasheet: STM32L476RG Clock Tree & Low-Power Stop2 Modes",
    category: "DATASHEET",
    subject: "EC3711",
    author: "Ashok Kumar A (2023MITEC042)",
    upvotes: 31,
    downloads: 205,
    url: "https://voltcore.annauniv.edu/repo/stm32l476_clock_annotated.pdf"
  }
];

// Seed Announcements (Feature 340)
const SEED_ANNOUNCEMENTS = [
  {
    id: "ann_01",
    title: "Anna University End-Semester Practical Examinations Schedule (Nov/Dec 2026)",
    category: "EXAM_TIMETABLE",
    priority: "URGENT",
    dept: "Controller of Examinations, Anna University",
    date: "2026-11-05",
    summary: "Practical and Viva-Voce examinations for B.E. ECE (Reg 2023) Semesters III and V commence on November 18, 2026. Hall tickets available on ACOE portal.",
    link: "https://acoe.annauniv.edu"
  },
  {
    id: "ann_02",
    title: "Texas Instruments Campus Placement & Summer Core Internship Drive",
    category: "PLACEMENT",
    priority: "IMPORTANT",
    dept: "CUIC / Placement Cell, MIT Campus",
    date: "2026-11-04",
    summary: "TI Analog & Embedded Firmware drive scheduled for pre-final and final year students. Shortlisting requires CGPA >= 8.25 and verified hardware projects.",
    link: "https://cuic.annauniv.edu"
  },
  {
    id: "ann_03",
    title: "IEEE MIT Student Branch: Hands-on Workshop on RISC-V Custom Instructions",
    category: "WORKSHOP",
    priority: "INFO",
    dept: "IEEE Student Branch, MIT Campus",
    date: "2026-11-03",
    summary: "Two-day workshop covering Chisel HDL, RISC-V GNU toolchain, and FPGA implementation of custom vector extensions. Certificates awarded.",
    link: "https://mitindia.edu/ieee"
  }
];

export default function CollaborationCommunityHub() {
  const [activeTab, setActiveTab] = useState('forums');

  // Tab 1: Forums & Subject Q&A state
  const [forumPosts, setForumPosts] = useState(SEED_FORUM_POSTS);
  const [selectedCategory, setSelectedCategory] = useState('ALL');
  const [selectedSubject, setSelectedSubject] = useState('ALL');
  const [newThreadTitle, setNewThreadTitle] = useState('');
  const [newThreadContent, setNewThreadContent] = useState('');
  const [newThreadCategory, setNewThreadCategory] = useState('VLSI');
  const [newThreadSubject, setNewThreadSubject] = useState('EC3552');
  const [newThreadTags, setNewThreadTags] = useState('VLSI, STA');
  const [expandedPostId, setExpandedPostId] = useState('post_01');
  const [replyInput, setReplyInput] = useState('');

  // Tab 2: Study Groups state
  const [studyGroups, setStudyGroups] = useState(SEED_STUDY_GROUPS);
  const [newGroupName, setNewGroupName] = useState('');
  const [newGroupSubject, setNewGroupSubject] = useState('EC3552 (VLSI and Chip Design)');
  const [newGroupTopic, setNewGroupTopic] = useState('');
  const [newGroupSchedule, setNewGroupSchedule] = useState('');
  const [userJoinedGroups, setUserJoinedGroups] = useState(['sg_01', 'sg_02']);

  // Tab 3: Notes & Peer Review state
  const [notes, setNotes] = useState(SEED_NOTES);
  const [activeNoteId, setActiveNoteId] = useState('note_01');
  const [isEditingNote, setIsEditingNote] = useState(false);
  const [noteContentEdit, setNoteContentEdit] = useState(SEED_NOTES[0].content);

  // Rubric Peer Review (Feature 335)
  const [circuitScore, setCircuitScore] = useState(8.5);
  const [simScore, setSimScore] = useState(8.0);
  const [docScore, setDocScore] = useState(9.0);
  const [reviewComments, setReviewComments] = useState('Well-documented transient response. Minor ripple on VDD rail could be improved with bypass decoupling.');
  const [reviewHistory, setReviewHistory] = useState([
    {
      id: "rev_01",
      title: "Lab 4: Op-Amp Second-Order Sallen-Key LPF",
      student: "Ashok Kumar A (2023MITEC042)",
      reviewer: "Kavitha R (2023MITEC055)",
      overall: 8.65,
      comments: "Excellent Butterworth damping and Monte Carlo simulation analysis."
    }
  ]);

  // Tab 4: Project Team Board state (Feature 336)
  const [projectTasks, setProjectTasks] = useState([
    { id: "task_1", desc: "Design 4-layer PCB for STM32L4 LoRa node with 50-ohm trace", assignee: "Ashok Kumar A", status: "DONE" },
    { id: "task_2", desc: "Implement FreeRTOS sleep mode with RTC alarm wakeup", assignee: "Kavitha R", status: "IN_PROGRESS" },
    { id: "task_3", desc: "Integrate AHT20 I2C temperature & humidity driver", assignee: "Dinesh S", status: "TODO" },
    { id: "task_4", desc: "Calibrate RF matching network on Vector Network Analyzer", assignee: "Ashok Kumar A", status: "TODO" }
  ]);
  const [newTaskDesc, setNewTaskDesc] = useState('');
  const [newTaskAssignee, setNewTaskAssignee] = useState('Ashok Kumar A');

  // Tab 5: Faculty Doubt Portal (Feature 337)
  const [facultyDoubts, setFacultyDoubts] = useState(SEED_DOUBTS);
  const [selectedFacultyId, setSelectedFacultyId] = useState('fac_01');
  const [doubtSubject, setDoubtSubject] = useState('EC3552');
  const [doubtText, setDoubtText] = useState('');
  const [doubtPriority, setDoubtPriority] = useState('MEDIUM');

  // Tab 6: Resources, Karma & Announcements (Features 338, 339, 340)
  const [resources, setResources] = useState(SEED_RESOURCES);
  const [resourceCategory, setResourceCategory] = useState('ALL');
  const [studentKarma, setStudentKarma] = useState({
    total: 125,
    vlsi: 65,
    embedded: 40,
    dsp: 20,
    badges: ["silicon_scholar", "rtos_champion", "apex_fellow"]
  });

  // Feature 331: Upvote thread
  const handleUpvoteThread = (postId) => {
    setForumPosts(posts => posts.map(p => {
      if (p.id === postId) {
        return { ...p, upvotes: p.upvotes + 1 };
      }
      return p;
    }));
    setStudentKarma(k => ({ ...k, total: k.total + 2 }));
  };

  // Feature 331: Post new thread
  const handleCreateThread = (e) => {
    e.preventDefault();
    if (!newThreadTitle.trim() || !newThreadContent.trim()) return;

    const newPost = {
      id: `post_${Date.now()}`,
      title: newThreadTitle,
      category: newThreadCategory,
      subject_code: newThreadSubject,
      author_name: "Ashok Kumar A",
      author_roll: "2023MITEC042",
      content: newThreadContent,
      tags: newThreadTags.split(',').map(t => t.trim()).filter(Boolean),
      upvotes: 0,
      created_at: new Date().toISOString(),
      replies: []
    };

    setForumPosts([newPost, ...forumPosts]);
    setNewThreadTitle('');
    setNewThreadContent('');
    setStudentKarma(k => ({ ...k, total: k.total + 5 }));
  };

  // Feature 331: Reply to thread
  const handleAddReply = (postId) => {
    if (!replyInput.trim()) return;

    const newReply = {
      id: `rep_${Date.now()}`,
      author_name: "Ashok Kumar A",
      author_roll: "2023MITEC042",
      content: replyInput,
      upvotes: 0,
      is_solution: false
    };

    setForumPosts(posts => posts.map(p => {
      if (p.id === postId) {
        return { ...p, replies: [...p.replies, newReply] };
      }
      return p;
    }));

    setReplyInput('');
    setStudentKarma(k => ({ ...k, total: k.total + 3 }));
  };

  // Feature 331: Mark solution
  const handleMarkSolution = (postId, replyId) => {
    setForumPosts(posts => posts.map(p => {
      if (p.id === postId) {
        return {
          ...p,
          replies: p.replies.map(r => ({ ...r, is_solution: r.id === replyId }))
        };
      }
      return p;
    }));
    setStudentKarma(k => ({ ...k, total: k.total + 15 }));
  };

  // Feature 333: Join / Leave Study Group
  const toggleJoinGroup = (groupId) => {
    if (userJoinedGroups.includes(groupId)) {
      setUserJoinedGroups(userJoinedGroups.filter(id => id !== groupId));
      setStudyGroups(groups => groups.map(g => {
        if (g.id === groupId) {
          return { ...g, members: g.members.filter(m => !m.includes("2023MITEC042")) };
        }
        return g;
      }));
    } else {
      const target = studyGroups.find(g => g.id === groupId);
      if (target && target.members.length >= target.max_members) {
        alert("This study group has reached maximum member capacity!");
        return;
      }
      setUserJoinedGroups([...userJoinedGroups, groupId]);
      setStudyGroups(groups => groups.map(g => {
        if (g.id === groupId) {
          return { ...g, members: [...g.members, "Ashok Kumar A (2023MITEC042)"] };
        }
        return g;
      }));
    }
  };

  // Feature 333: Create Study Group
  const handleCreateGroup = (e) => {
    e.preventDefault();
    if (!newGroupName.trim() || !newGroupTopic.trim()) return;

    const newGroup = {
      id: `sg_${Date.now()}`,
      name: newGroupName,
      subject: newGroupSubject,
      topic: newGroupTopic,
      max_members: 6,
      members: ["Ashok Kumar A (2023MITEC042)"],
      schedule: newGroupSchedule || "Schedule TBD",
      room_url: `https://meet.jit.si/voltcore-${Date.now()}`
    };

    setStudyGroups([newGroup, ...studyGroups]);
    setUserJoinedGroups([...userJoinedGroups, newGroup.id]);
    setNewGroupName('');
    setNewGroupTopic('');
    setNewGroupSchedule('');
    setStudentKarma(k => ({ ...k, total: k.total + 10 }));
  };

  // Feature 335: Submit Peer Review
  const overallRubricScore = (0.40 * circuitScore + 0.35 * simScore + 0.25 * docScore).toFixed(2);
  const handleSubmitReview = (e) => {
    e.preventDefault();
    const newRev = {
      id: `rev_${Date.now()}`,
      title: "Lab 5: Verilog HDL UART & Baud Generator",
      student: "Dinesh S (2023MITEC010)",
      reviewer: "Ashok Kumar A (2023MITEC042)",
      overall: parseFloat(overallRubricScore),
      comments: reviewComments
    };
    setReviewHistory([newRev, ...reviewHistory]);
    setStudentKarma(k => ({ ...k, total: k.total + 10 }));
    alert(`Peer Review submitted! Overall Rubric Score: ${overallRubricScore}/10.0 (+10 Karma Awarded)`);
  };

  // Feature 336: Toggle Task Status
  const handleToggleTaskStatus = (taskId) => {
    const statusCycle = { 'TODO': 'IN_PROGRESS', 'IN_PROGRESS': 'DONE', 'DONE': 'TODO' };
    setProjectTasks(tasks => tasks.map(t => {
      if (t.id === taskId) {
        return { ...t, status: statusCycle[t.status] };
      }
      return t;
    }));
  };

  const handleAddTask = (e) => {
    e.preventDefault();
    if (!newTaskDesc.trim()) return;
    const newTask = {
      id: `task_${Date.now()}`,
      desc: newTaskDesc,
      assignee: newTaskAssignee,
      status: 'TODO'
    };
    setProjectTasks([...projectTasks, newTask]);
    setNewTaskDesc('');
  };

  // Feature 337: Submit Faculty Doubt
  const handleSubmitDoubt = (e) => {
    e.preventDefault();
    if (!doubtText.trim()) return;
    const fac = FACULTY_LIST.find(f => f.id === selectedFacultyId);
    const newDoubt = {
      id: `dbt_${Date.now()}`,
      student_roll: "2023MITEC042",
      faculty_id: selectedFacultyId,
      faculty_name: fac ? fac.name : "Faculty Member",
      subject_code: doubtSubject,
      query: doubtText,
      priority: doubtPriority,
      status: "PENDING",
      response: null
    };
    setFacultyDoubts([newDoubt, ...facultyDoubts]);
    setDoubtText('');
    alert(`Query routed directly to ${fac ? fac.name : "Faculty"}. You will receive notification during faculty office hours.`);
  };

  // Feature 338: Upvote Resource
  const handleUpvoteResource = (resId) => {
    setResources(res => res.map(r => {
      if (r.id === resId) {
        return { ...r, upvotes: r.upvotes + 1 };
      }
      return r;
    }));
  };

  const filteredPosts = forumPosts.filter(p => {
    const matchCat = (selectedCategory === 'ALL' || p.category === selectedCategory);
    const matchSubj = (selectedSubject === 'ALL' || p.subject_code === selectedSubject);
    return matchCat && matchSubj;
  });

  const filteredResources = resources.filter(r => {
    return resourceCategory === 'ALL' || r.category === resourceCategory;
  });

  return (
    <div className="collaboration-hub space-y-6">
      {/* Platform Header */}
      <div className="bg-slate-900/80 border border-cyan-500/30 rounded-2xl p-6 backdrop-blur-md shadow-2xl relative overflow-hidden">
        <div className="absolute top-0 right-0 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none -mr-20 -mt-20"></div>
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 relative z-10">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <span className="px-3 py-1 text-xs font-bold rounded-full bg-cyan-500/20 text-cyan-400 border border-cyan-500/40">
                PHASE M • COMMUNITY & COLLABORATION
              </span>
              <span className="px-3 py-1 text-xs font-bold rounded-full bg-purple-500/20 text-purple-400 border border-purple-500/40">
                ANNA UNIV REG 2023
              </span>
            </div>
            <h1 className="text-3xl font-extrabold text-white tracking-tight">
              ECE Peer Collaboration & Academic Commons
            </h1>
            <p className="text-sm text-slate-400 mt-1">
              Madras Institute of Technology (MIT Campus) • Department of Electronics Engineering
            </p>
          </div>
          <div className="flex items-center gap-3 bg-slate-800/80 border border-slate-700/60 p-3 rounded-xl">
            <div className="text-right">
              <div className="text-xs text-slate-400">Knowledge Karma</div>
              <div className="text-xl font-black text-cyan-400">{studentKarma.total} pts</div>
            </div>
            <div className="w-10 h-10 rounded-lg bg-gradient-to-tr from-cyan-500 to-blue-600 flex items-center justify-center text-white font-bold text-sm shadow-lg">
              AK
            </div>
          </div>
        </div>

        {/* Navigation Tabs */}
        <div className="flex flex-wrap gap-2 mt-6 border-t border-slate-800/80 pt-4">
          {[
            { id: 'forums', label: 'Discussion Forums & Q&A', icon: '💬' },
            { id: 'study_groups', label: 'Study Groups & Virtual Rooms', icon: '👥' },
            { id: 'notes_review', label: 'Collaborative Notes & Peer Review', icon: '📝' },
            { id: 'project_boards', label: 'Project Sprint Boards', icon: '⚡' },
            { id: 'faculty_portal', label: 'Faculty Doubt Portal', icon: '🎓' },
            { id: 'resources_karma', label: 'Shared Library & Karma', icon: '🏆' }
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-4 py-2 rounded-xl text-sm font-semibold transition-all duration-200 flex items-center gap-2 ${
                activeTab === tab.id
                  ? 'bg-cyan-500 text-slate-950 font-bold shadow-lg shadow-cyan-500/20'
                  : 'bg-slate-800/60 text-slate-300 hover:bg-slate-700/80 hover:text-white border border-slate-700/40'
              }`}
            >
              <span>{tab.icon}</span>
              <span>{tab.label}</span>
            </button>
          ))}
        </div>
      </div>

      {/* =========================================================================
          TAB 1: STUDENT DISCUSSION FORUMS & SUBJECT Q&A (Features 331 & 332)
      ========================================================================= */}
      {activeTab === 'forums' && (
        <div className="space-y-6">
          {/* Filter Bar & Controls */}
          <div className="bg-slate-900/60 border border-slate-800 p-4 rounded-xl flex flex-wrap gap-4 items-center justify-between">
            <div className="flex flex-wrap items-center gap-2">
              <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Domain:</span>
              {['ALL', 'VLSI', 'Embedded', 'Analog', 'Signals', 'RF'].map(cat => (
                <button
                  key={cat}
                  onClick={() => setSelectedCategory(cat)}
                  className={`px-3 py-1 text-xs rounded-lg font-medium transition ${
                    selectedCategory === cat
                      ? 'bg-cyan-500 text-slate-950 font-bold'
                      : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
                  }`}
                >
                  {cat}
                </button>
              ))}
            </div>

            <div className="flex items-center gap-2">
              <span className="text-xs font-semibold text-slate-400">Subject Code:</span>
              <select
                value={selectedSubject}
                onChange={e => setSelectedSubject(e.target.value)}
                className="bg-slate-800 border border-slate-700 text-slate-200 text-xs rounded-lg px-2.5 py-1.5 focus:outline-none focus:border-cyan-500"
              >
                <option value="ALL">All Anna Univ Subjects</option>
                {REG2023_SUBJECTS.map(s => (
                  <option key={s.code} value={s.code}>{s.code} - {s.name} (Sem {s.sem})</option>
                ))}
              </select>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Thread List & Discussion View */}
            <div className="lg:col-span-2 space-y-4">
              {filteredPosts.map(post => (
                <div
                  key={post.id}
                  className="bg-slate-900/80 border border-slate-800 rounded-xl p-5 hover:border-slate-700 transition"
                >
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1.5">
                        <span className="px-2 py-0.5 text-xs font-bold rounded bg-cyan-500/20 text-cyan-400 border border-cyan-500/30">
                          {post.subject_code}
                        </span>
                        <span className="px-2 py-0.5 text-xs font-semibold rounded bg-purple-500/20 text-purple-300">
                          {post.category}
                        </span>
                        <span className="text-xs text-slate-400">by {post.author_name} ({post.author_roll})</span>
                      </div>
                      <h3 className="text-lg font-bold text-white hover:text-cyan-400 transition cursor-pointer" onClick={() => setExpandedPostId(post.id)}>
                        {post.title}
                      </h3>
                      <p className="text-sm text-slate-300 mt-2 leading-relaxed">
                        {post.content}
                      </p>
                      <div className="flex flex-wrap gap-1.5 mt-3">
                        {post.tags.map(t => (
                          <span key={t} className="text-xs px-2 py-0.5 rounded bg-slate-800 text-slate-400 border border-slate-700/50">
                            #{t}
                          </span>
                        ))}
                      </div>
                    </div>

                    <div className="flex flex-col items-center justify-center bg-slate-800/80 border border-slate-700/60 rounded-xl px-3 py-2 min-w-[56px]">
                      <button
                        onClick={() => handleUpvoteThread(post.id)}
                        className="text-cyan-400 hover:text-cyan-300 font-bold text-sm transform hover:-translate-y-0.5 transition"
                        title="Upvote thread (+2 Karma)"
                      >
                        ▲
                      </button>
                      <span className="text-sm font-extrabold text-white">{post.upvotes}</span>
                      <span className="text-[10px] text-slate-400 uppercase tracking-wider">votes</span>
                    </div>
                  </div>

                  {/* Replies Section */}
                  {expandedPostId === post.id && (
                    <div className="mt-5 border-t border-slate-800 pt-4 space-y-3">
                      <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider">
                        Peer Responses ({post.replies.length})
                      </h4>

                      {post.replies.map(rep => (
                        <div
                          key={rep.id}
                          className={`p-3.5 rounded-xl border text-sm ${
                            rep.is_solution
                              ? 'bg-emerald-950/20 border-emerald-500/40 text-emerald-100'
                              : 'bg-slate-800/50 border-slate-700/50 text-slate-200'
                          }`}
                        >
                          <div className="flex items-center justify-between mb-1.5">
                            <span className="font-semibold text-white text-xs">
                              {rep.author_name} ({rep.author_roll})
                            </span>
                            {rep.is_solution && (
                              <span className="px-2 py-0.5 text-[11px] font-bold rounded-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/40">
                                ✓ Verified Solution
                              </span>
                            )}
                          </div>
                          <p className="text-sm leading-relaxed">{rep.content}</p>

                          {!rep.is_solution && (
                            <button
                              onClick={() => handleMarkSolution(post.id, rep.id)}
                              className="mt-2 text-xs text-cyan-400 hover:underline font-semibold"
                            >
                              Mark as Accepted Solution (+15 Karma)
                            </button>
                          )}
                        </div>
                      ))}

                      {/* Reply Input */}
                      <div className="flex gap-2 pt-2">
                        <input
                          type="text"
                          value={replyInput}
                          onChange={e => setReplyInput(e.target.value)}
                          placeholder="Provide an engineering explanation or solution..."
                          className="flex-1 bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500"
                        />
                        <button
                          onClick={() => handleAddReply(post.id)}
                          className="px-4 py-2 bg-cyan-500 text-slate-950 font-bold rounded-lg text-xs hover:bg-cyan-400 transition"
                        >
                          Reply
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>

            {/* Create New Thread Widget */}
            <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-5 h-fit sticky top-6">
              <h3 className="text-base font-bold text-white mb-3 flex items-center gap-2">
                <span>➕</span> Post ECE Technical Thread
              </h3>
              <form onSubmit={handleCreateThread} className="space-y-3">
                <div>
                  <label className="block text-xs font-semibold text-slate-400 mb-1">Title</label>
                  <input
                    type="text"
                    value={newThreadTitle}
                    onChange={e => setNewThreadTitle(e.target.value)}
                    placeholder="e.g. S-Parameter matching on FR4 substrate"
                    className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-cyan-500"
                    required
                  />
                </div>

                <div className="grid grid-cols-2 gap-2">
                  <div>
                    <label className="block text-xs font-semibold text-slate-400 mb-1">Domain</label>
                    <select
                      value={newThreadCategory}
                      onChange={e => setNewThreadCategory(e.target.value)}
                      className="w-full bg-slate-800 border border-slate-700 rounded-lg px-2.5 py-2 text-xs text-white focus:outline-none focus:border-cyan-500"
                    >
                      <option value="VLSI">VLSI & Chip Design</option>
                      <option value="Embedded">Embedded & RTOS</option>
                      <option value="Analog">Analog & LIC</option>
                      <option value="Signals">Signals & DSP</option>
                      <option value="RF">RF & Antennas</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-slate-400 mb-1">Subject</label>
                    <select
                      value={newThreadSubject}
                      onChange={e => setNewThreadSubject(e.target.value)}
                      className="w-full bg-slate-800 border border-slate-700 rounded-lg px-2.5 py-2 text-xs text-white focus:outline-none focus:border-cyan-500"
                    >
                      {REG2023_SUBJECTS.map(s => (
                        <option key={s.code} value={s.code}>{s.code}</option>
                      ))}
                    </select>
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-400 mb-1">Technical Question / Description</label>
                  <textarea
                    value={newThreadContent}
                    onChange={e => setNewThreadContent(e.target.value)}
                    rows={4}
                    placeholder="Include circuit parameters, equations, or timing constraints..."
                    className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-cyan-500"
                    required
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-400 mb-1">Tags (comma-separated)</label>
                  <input
                    type="text"
                    value={newThreadTags}
                    onChange={e => setNewThreadTags(e.target.value)}
                    placeholder="e.g. SallenKey, OpAmp, LTspice"
                    className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-cyan-500"
                  />
                </div>

                <button
                  type="submit"
                  className="w-full py-2.5 bg-gradient-to-r from-cyan-500 to-blue-600 text-slate-950 font-bold rounded-lg text-xs hover:from-cyan-400 hover:to-blue-500 transition shadow-lg shadow-cyan-500/20"
                >
                  Publish Thread (+5 Karma)
                </button>
              </form>
            </div>
          </div>
        </div>
      )}

      {/* =========================================================================
          TAB 2: STUDY GROUP CREATOR & VIRTUAL ROOMS (Feature 333)
      ========================================================================= */}
      {activeTab === 'study_groups' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-4">
            <div className="bg-slate-900/60 border border-slate-800 p-4 rounded-xl flex items-center justify-between">
              <div>
                <h2 className="text-lg font-bold text-white">Active Peer Study Cohorts</h2>
                <p className="text-xs text-slate-400">Join real-time study sessions with synchronized virtual Jitsi meeting rooms</p>
              </div>
              <span className="px-3 py-1 bg-cyan-500/20 text-cyan-400 border border-cyan-500/40 text-xs font-bold rounded-full">
                {studyGroups.length} Active Cohorts
              </span>
            </div>

            <div className="space-y-4">
              {studyGroups.map(grp => {
                const isMember = userJoinedGroups.includes(grp.id);
                const isFull = grp.members.length >= grp.max_members;

                return (
                  <div key={grp.id} className="bg-slate-900/80 border border-slate-800 rounded-xl p-5 hover:border-slate-700 transition">
                    <div className="flex flex-col md:flex-row md:items-start justify-between gap-4">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1.5">
                          <span className="px-2.5 py-0.5 rounded text-xs font-bold bg-cyan-500/20 text-cyan-400 border border-cyan-500/40">
                            {grp.subject}
                          </span>
                          <span className="text-xs text-slate-400">📅 {grp.schedule}</span>
                        </div>
                        <h3 className="text-lg font-bold text-white">{grp.name}</h3>
                        <p className="text-sm text-slate-300 mt-1">{grp.topic}</p>

                        <div className="mt-3">
                          <div className="text-xs font-semibold text-slate-400 mb-1">
                            Members ({grp.members.length}/{grp.max_members}):
                          </div>
                          <div className="flex flex-wrap gap-1.5">
                            {grp.members.map((m, idx) => (
                              <span key={idx} className="text-xs px-2.5 py-1 rounded-md bg-slate-800 text-slate-300 border border-slate-700/60">
                                👤 {m}
                              </span>
                            ))}
                          </div>
                        </div>
                      </div>

                      <div className="flex flex-col gap-2 min-w-[140px]">
                        <button
                          onClick={() => toggleJoinGroup(grp.id)}
                          className={`w-full py-2 rounded-lg text-xs font-bold transition ${
                            isMember
                              ? 'bg-rose-500/20 border border-rose-500/40 text-rose-300 hover:bg-rose-500/30'
                              : isFull
                              ? 'bg-slate-800 text-slate-500 cursor-not-allowed border border-slate-700'
                              : 'bg-cyan-500 text-slate-950 hover:bg-cyan-400 shadow-md shadow-cyan-500/20'
                          }`}
                        >
                          {isMember ? 'Leave Group' : isFull ? 'Group Full' : 'Join Group'}
                        </button>

                        {isMember && (
                          <a
                            href={grp.room_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="w-full py-2 bg-purple-600 hover:bg-purple-500 text-white rounded-lg text-xs font-bold text-center transition flex items-center justify-center gap-1.5"
                          >
                            <span>🎥</span> Launch Room
                          </a>
                        )}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Create Study Group */}
          <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-5 h-fit">
            <h3 className="text-base font-bold text-white mb-3 flex items-center gap-2">
              <span>👥</span> Form a Study Cohort
            </h3>
            <form onSubmit={handleCreateGroup} className="space-y-3">
              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">Group Name</label>
                <input
                  type="text"
                  value={newGroupName}
                  onChange={e => setNewGroupName(e.target.value)}
                  placeholder="e.g. S-Parameter & RF Matching Circle"
                  className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-cyan-500"
                  required
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">Subject</label>
                <select
                  value={newGroupSubject}
                  onChange={e => setNewGroupSubject(e.target.value)}
                  className="w-full bg-slate-800 border border-slate-700 rounded-lg px-2.5 py-2 text-xs text-white focus:outline-none focus:border-cyan-500"
                >
                  {REG2023_SUBJECTS.map(s => (
                    <option key={s.code} value={`${s.code} (${s.name})`}>{s.code} - {s.name}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">Target Topic</label>
                <input
                  type="text"
                  value={newGroupTopic}
                  onChange={e => setNewGroupTopic(e.target.value)}
                  placeholder="e.g. Sallen-Key low-pass filter LTspice design"
                  className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-cyan-500"
                  required
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">Meeting Schedule</label>
                <input
                  type="text"
                  value={newGroupSchedule}
                  onChange={e => setNewGroupSchedule(e.target.value)}
                  placeholder="e.g. Mon & Wed • 19:00 – 20:30 IST"
                  className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-cyan-500"
                  required
                />
              </div>

              <button
                type="submit"
                className="w-full py-2.5 bg-gradient-to-r from-purple-500 to-indigo-600 text-white font-bold rounded-lg text-xs hover:from-purple-400 hover:to-indigo-500 transition shadow-lg shadow-purple-500/20"
              >
                Create Cohort (+10 Karma)
              </button>
            </form>
          </div>
        </div>
      )}

      {/* =========================================================================
          TAB 3: COLLABORATIVE NOTES & PEER ASSIGNMENT REVIEW (Features 334 & 335)
      ========================================================================= */}
      {activeTab === 'notes_review' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Section 1: Collaborative Notes Workspace (Feature 334) */}
          <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-5 space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-lg font-bold text-white flex items-center gap-2">
                  <span>📝</span> Collaborative Notes Workspace
                </h2>
                <p className="text-xs text-slate-400">Live markdown lecture summaries with version history</p>
              </div>
              <div className="flex gap-2">
                {notes.map(n => (
                  <button
                    key={n.id}
                    onClick={() => {
                      setActiveNoteId(n.id);
                      setNoteContentEdit(n.content);
                      setIsEditingNote(false);
                    }}
                    className={`px-3 py-1 rounded-lg text-xs font-semibold transition ${
                      activeNoteId === n.id
                        ? 'bg-cyan-500 text-slate-950 font-bold'
                        : 'bg-slate-800 text-slate-300'
                    }`}
                  >
                    {n.subject}
                  </button>
                ))}
              </div>
            </div>

            {(() => {
              const currentNote = notes.find(n => n.id === activeNoteId) || notes[0];
              return (
                <div className="space-y-3">
                  <div className="flex items-center justify-between bg-slate-800/60 p-3 rounded-lg border border-slate-700/50">
                    <div>
                      <div className="text-sm font-bold text-white">{currentNote.title}</div>
                      <div className="text-xs text-slate-400">
                        Version {currentNote.version} • Authors: {currentNote.authors.join(", ")}
                      </div>
                    </div>
                    <button
                      onClick={() => setIsEditingNote(!isEditingNote)}
                      className="px-3 py-1.5 bg-slate-700 hover:bg-slate-600 text-white text-xs font-semibold rounded-lg transition"
                    >
                      {isEditingNote ? 'Preview' : 'Edit Note'}
                    </button>
                  </div>

                  {isEditingNote ? (
                    <div>
                      <textarea
                        value={noteContentEdit}
                        onChange={e => setNoteContentEdit(e.target.value)}
                        rows={12}
                        className="w-full bg-slate-950 border border-slate-700 rounded-lg p-3 text-xs text-cyan-300 font-mono focus:outline-none focus:border-cyan-500"
                      />
                      <button
                        onClick={() => {
                          setNotes(notes.map(n => {
                            if (n.id === currentNote.id) {
                              return {
                                ...n,
                                version: n.version + 1,
                                content: noteContentEdit,
                                authors: Array.from(new Set([...n.authors, "Ashok Kumar A"]))
                              };
                            }
                            return n;
                          }));
                          setIsEditingNote(false);
                          setStudentKarma(k => ({ ...k, total: k.total + 5 }));
                        }}
                        className="mt-2 px-4 py-2 bg-cyan-500 text-slate-950 font-bold text-xs rounded-lg hover:bg-cyan-400 transition"
                      >
                        Save Revision (Increment to v{currentNote.version + 1})
                      </button>
                    </div>
                  ) : (
                    <div className="bg-slate-950/70 border border-slate-800 rounded-lg p-4 font-mono text-xs text-slate-200 whitespace-pre-wrap leading-relaxed max-h-80 overflow-y-auto">
                      {currentNote.content}
                    </div>
                  )}
                </div>
              );
            })()}
          </div>

          {/* Section 2: Rubric-Based Peer Assignment Review (Feature 335) */}
          <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-5 space-y-4">
            <div>
              <h2 className="text-lg font-bold text-white flex items-center gap-2">
                <span>⚖️</span> Peer Assignment Review System
              </h2>
              <p className="text-xs text-slate-400">Rubric formula: 40% Circuit + 35% Simulation + 25% Documentation</p>
            </div>

            <form onSubmit={handleSubmitReview} className="space-y-4 bg-slate-800/40 p-4 rounded-xl border border-slate-700/50">
              <div className="text-xs font-semibold text-cyan-400">
                Evaluating: <span className="text-white">Lab 5: Verilog HDL UART & Baud Generator</span>
              </div>

              {/* Sliders */}
              <div className="space-y-3">
                <div>
                  <div className="flex justify-between text-xs font-medium text-slate-300 mb-1">
                    <span>Circuit Architecture & Design (40%)</span>
                    <span className="font-bold text-cyan-400">{circuitScore} / 10.0</span>
                  </div>
                  <input
                    type="range"
                    min="0"
                    max="10"
                    step="0.5"
                    value={circuitScore}
                    onChange={e => setCircuitScore(parseFloat(e.target.value))}
                    className="w-full accent-cyan-400"
                  />
                </div>

                <div>
                  <div className="flex justify-between text-xs font-medium text-slate-300 mb-1">
                    <span>Simulation & Testbench Accuracy (35%)</span>
                    <span className="font-bold text-purple-400">{simScore} / 10.0</span>
                  </div>
                  <input
                    type="range"
                    min="0"
                    max="10"
                    step="0.5"
                    value={simScore}
                    onChange={e => setSimScore(parseFloat(e.target.value))}
                    className="w-full accent-purple-400"
                  />
                </div>

                <div>
                  <div className="flex justify-between text-xs font-medium text-slate-300 mb-1">
                    <span>Engineering Documentation (25%)</span>
                    <span className="font-bold text-emerald-400">{docScore} / 10.0</span>
                  </div>
                  <input
                    type="range"
                    min="0"
                    max="10"
                    step="0.5"
                    value={docScore}
                    onChange={e => setDocScore(parseFloat(e.target.value))}
                    className="w-full accent-emerald-400"
                  />
                </div>
              </div>

              {/* Calculated Score Meter */}
              <div className="bg-slate-900 border border-slate-700 p-3 rounded-lg flex items-center justify-between">
                <div>
                  <div className="text-xs text-slate-400">Weighted Rubric Score</div>
                  <div className="text-2xl font-black text-cyan-400">{overallRubricScore} <span className="text-xs text-slate-400">/ 10.0</span></div>
                </div>
                <span className={`px-3 py-1 rounded-full text-xs font-bold border ${
                  parseFloat(overallRubricScore) >= 8.5
                    ? 'bg-emerald-500/20 text-emerald-400 border-emerald-500/40'
                    : 'bg-cyan-500/20 text-cyan-400 border-cyan-500/40'
                }`}>
                  {parseFloat(overallRubricScore) >= 8.5 ? 'DISTINCTION GRADE' : 'FIRST CLASS'}
                </span>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">Constructive Feedback</label>
                <textarea
                  value={reviewComments}
                  onChange={e => setReviewComments(e.target.value)}
                  rows={2}
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2.5 text-xs text-white focus:outline-none focus:border-cyan-500"
                  required
                />
              </div>

              <button
                type="submit"
                className="w-full py-2 bg-gradient-to-r from-emerald-500 to-teal-600 text-slate-950 font-bold rounded-lg text-xs hover:from-emerald-400 hover:to-teal-500 transition shadow-lg shadow-emerald-500/20"
              >
                Submit Peer Review (+10 Karma)
              </button>
            </form>
          </div>
        </div>
      )}

      {/* =========================================================================
          TAB 4: PROJECT TEAM DISCUSSION & SPRINT BOARDS (Feature 336)
      ========================================================================= */}
      {activeTab === 'project_boards' && (
        <div className="space-y-6">
          <div className="bg-slate-900/60 border border-slate-800 p-4 rounded-xl flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div>
              <h2 className="text-lg font-bold text-white flex items-center gap-2">
                <span>⚡</span> Project Sprint Board: Edge LoRa Node
              </h2>
              <p className="text-xs text-slate-400">Inter-student hardware sprint board with real-time status management</p>
            </div>

            <form onSubmit={handleAddTask} className="flex gap-2">
              <input
                type="text"
                value={newTaskDesc}
                onChange={e => setNewTaskDesc(e.target.value)}
                placeholder="New sprint task description..."
                className="bg-slate-800 border border-slate-700 rounded-lg px-3 py-1.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500 min-w-[240px]"
              />
              <button
                type="submit"
                className="px-4 py-1.5 bg-cyan-500 text-slate-950 font-bold rounded-lg text-xs hover:bg-cyan-400 transition"
              >
                Add Task
              </button>
            </form>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {['TODO', 'IN_PROGRESS', 'DONE'].map(statusCol => {
              const colTasks = projectTasks.filter(t => t.status === statusCol);
              const colColors = {
                TODO: 'border-slate-700 bg-slate-900/40 text-slate-400',
                IN_PROGRESS: 'border-amber-500/40 bg-amber-950/10 text-amber-400',
                DONE: 'border-emerald-500/40 bg-emerald-950/10 text-emerald-400'
              };

              return (
                <div key={statusCol} className="bg-slate-900/80 border border-slate-800 rounded-xl p-4 flex flex-col">
                  <div className="flex items-center justify-between mb-3 pb-2 border-b border-slate-800">
                    <span className={`text-xs font-bold uppercase tracking-wider ${colColors[statusCol].split(' ')[2]}`}>
                      {statusCol.replace('_', ' ')}
                    </span>
                    <span className="text-xs px-2 py-0.5 rounded-full bg-slate-800 text-slate-300 font-bold">
                      {colTasks.length}
                    </span>
                  </div>

                  <div className="space-y-3 flex-1">
                    {colTasks.map(task => (
                      <div
                        key={task.id}
                        onClick={() => handleToggleTaskStatus(task.id)}
                        className="bg-slate-800/80 hover:bg-slate-800 border border-slate-700/60 rounded-lg p-3 cursor-pointer transition transform hover:-translate-y-0.5 shadow-sm"
                        title="Click to cycle status: TODO -> IN PROGRESS -> DONE"
                      >
                        <p className="text-xs text-white font-medium mb-2 leading-relaxed">{task.desc}</p>
                        <div className="flex items-center justify-between text-[11px] text-slate-400">
                          <span>👤 {task.assignee}</span>
                          <span className="text-[10px] text-cyan-400 font-bold underline">Cycle Status ↻</span>
                        </div>
                      </div>
                    ))}
                    {colTasks.length === 0 && (
                      <div className="text-center py-6 text-xs text-slate-500 italic">No tasks in this column</div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* =========================================================================
          TAB 5: FACULTY DOUBT-CLEARING PORTAL (Feature 337)
      ========================================================================= */}
      {activeTab === 'faculty_portal' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-4">
            <div className="bg-slate-900/60 border border-slate-800 p-4 rounded-xl">
              <h2 className="text-lg font-bold text-white flex items-center gap-2">
                <span>🎓</span> Faculty Doubt-Clearing Queue
              </h2>
              <p className="text-xs text-slate-400">Direct technical inquiries to MIT Campus ECE professors & research guides</p>
            </div>

            <div className="space-y-4">
              {facultyDoubts.map(dbt => (
                <div key={dbt.id} className="bg-slate-900/80 border border-slate-800 rounded-xl p-5 hover:border-slate-700 transition">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <span className="px-2.5 py-0.5 rounded text-xs font-bold bg-cyan-500/20 text-cyan-400 border border-cyan-500/40">
                        {dbt.subject_code}
                      </span>
                      <span className="text-xs font-semibold text-white">To: {dbt.faculty_name}</span>
                    </div>
                    <span className={`px-2 py-0.5 text-[11px] font-bold rounded-full ${
                      dbt.status === 'RESOLVED'
                        ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/40'
                        : 'bg-amber-500/20 text-amber-400 border border-amber-500/40'
                    }`}>
                      {dbt.status}
                    </span>
                  </div>

                  <p className="text-sm text-slate-200 mt-1 leading-relaxed">
                    <span className="font-semibold text-slate-400">Query: </span>
                    {dbt.query}
                  </p>

                  {dbt.response && (
                    <div className="mt-3 p-3 bg-cyan-950/20 border border-cyan-500/40 rounded-lg text-xs text-cyan-100">
                      <div className="font-bold text-cyan-400 mb-1 flex items-center gap-1.5">
                        <span>✓</span> Verified Faculty Response ({dbt.faculty_name})
                      </div>
                      <p className="leading-relaxed">{dbt.response}</p>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Submit Question to Faculty */}
          <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-5 h-fit">
            <h3 className="text-base font-bold text-white mb-3 flex items-center gap-2">
              <span>✉️</span> Submit Academic Query
            </h3>
            <form onSubmit={handleSubmitDoubt} className="space-y-3">
              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">Select Professor</label>
                <select
                  value={selectedFacultyId}
                  onChange={e => setSelectedFacultyId(e.target.value)}
                  className="w-full bg-slate-800 border border-slate-700 rounded-lg px-2.5 py-2 text-xs text-white focus:outline-none focus:border-cyan-500"
                >
                  {FACULTY_LIST.map(f => (
                    <option key={f.id} value={f.id}>{f.name} ({f.spec})</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">Subject</label>
                <select
                  value={doubtSubject}
                  onChange={e => setDoubtSubject(e.target.value)}
                  className="w-full bg-slate-800 border border-slate-700 rounded-lg px-2.5 py-2 text-xs text-white focus:outline-none focus:border-cyan-500"
                >
                  {REG2023_SUBJECTS.map(s => (
                    <option key={s.code} value={s.code}>{s.code} - {s.name}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">Priority</label>
                <select
                  value={doubtPriority}
                  onChange={e => setDoubtPriority(e.target.value)}
                  className="w-full bg-slate-800 border border-slate-700 rounded-lg px-2.5 py-2 text-xs text-white focus:outline-none focus:border-cyan-500"
                >
                  <option value="LOW">Low (General Curiosity)</option>
                  <option value="MEDIUM">Medium (Lab Assignment)</option>
                  <option value="HIGH">High (Exam/Thesis Concept)</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">Technical Question</label>
                <textarea
                  value={doubtText}
                  onChange={e => setDoubtText(e.target.value)}
                  rows={4}
                  placeholder="Detail your question with specific equation or circuit references..."
                  className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-cyan-500"
                  required
                />
              </div>

              <button
                type="submit"
                className="w-full py-2.5 bg-gradient-to-r from-blue-500 to-indigo-600 text-white font-bold rounded-lg text-xs hover:from-blue-400 hover:to-indigo-500 transition shadow-lg shadow-blue-500/20"
              >
                Dispatch to Professor's Queue
              </button>
            </form>
          </div>
        </div>
      )}

      {/* =========================================================================
          TAB 6: SHARED RESOURCE LIBRARY, KARMA & ANNOUNCEMENTS (Features 338, 339, 340)
      ========================================================================= */}
      {activeTab === 'resources_karma' && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Feature 339: Student Karma Profile & Leaderboard */}
            <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-5 space-y-4">
              <h2 className="text-base font-bold text-white flex items-center gap-2">
                <span>🏆</span> Student Karma & Badges (Feature 339)
              </h2>

              <div className="bg-slate-800/60 p-4 rounded-xl border border-slate-700/60 text-center">
                <div className="text-xs text-slate-400 uppercase tracking-wider">Total Contribution Points</div>
                <div className="text-3xl font-black text-cyan-400 mt-1">{studentKarma.total} pts</div>
                <div className="text-xs text-slate-400 mt-1">Lead: Ashok Kumar A (2023MITEC042)</div>

                <div className="grid grid-cols-3 gap-2 mt-4 text-center">
                  <div className="bg-slate-900 p-2 rounded-lg border border-slate-800">
                    <div className="text-[10px] text-slate-400">VLSI</div>
                    <div className="text-sm font-bold text-cyan-300">{studentKarma.vlsi} pts</div>
                  </div>
                  <div className="bg-slate-900 p-2 rounded-lg border border-slate-800">
                    <div className="text-[10px] text-slate-400">Embedded</div>
                    <div className="text-sm font-bold text-purple-300">{studentKarma.embedded} pts</div>
                  </div>
                  <div className="bg-slate-900 p-2 rounded-lg border border-slate-800">
                    <div className="text-[10px] text-slate-400">Signals</div>
                    <div className="text-sm font-bold text-emerald-300">{studentKarma.dsp} pts</div>
                  </div>
                </div>
              </div>

              <div>
                <div className="text-xs font-semibold text-slate-400 mb-2">Unlocked Honor Badges</div>
                <div className="flex flex-wrap gap-2">
                  <span className="px-3 py-1 bg-cyan-500/20 text-cyan-400 border border-cyan-500/40 text-xs font-bold rounded-lg flex items-center gap-1.5">
                    <span>⚡</span> Silicon Scholar (50+ VLSI)
                  </span>
                  <span className="px-3 py-1 bg-purple-500/20 text-purple-400 border border-purple-500/40 text-xs font-bold rounded-lg flex items-center gap-1.5">
                    <span>⚙️</span> RTOS Champion
                  </span>
                  <span className="px-3 py-1 bg-amber-500/20 text-amber-400 border border-amber-500/40 text-xs font-bold rounded-lg flex items-center gap-1.5">
                    <span>👑</span> VoltCore Apex Fellow
                  </span>
                </div>
              </div>
            </div>

            {/* Feature 340: Academic Announcement Feed */}
            <div className="lg:col-span-2 bg-slate-900/80 border border-slate-800 rounded-xl p-5 space-y-4">
              <h2 className="text-base font-bold text-white flex items-center gap-2">
                <span>📢</span> Academic Announcement Feed (Feature 340)
              </h2>

              <div className="space-y-3">
                {SEED_ANNOUNCEMENTS.map(ann => (
                  <div key={ann.id} className="bg-slate-800/60 border border-slate-700/60 rounded-xl p-4 hover:border-slate-600 transition">
                    <div className="flex items-center justify-between gap-2 mb-1.5">
                      <div className="flex items-center gap-2">
                        <span className={`px-2 py-0.5 text-[11px] font-bold rounded ${
                          ann.priority === 'URGENT'
                            ? 'bg-rose-500/20 text-rose-400 border border-rose-500/40'
                            : 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/40'
                        }`}>
                          {ann.priority}
                        </span>
                        <span className="text-xs text-slate-400">📅 {ann.date}</span>
                      </div>
                      <span className="text-xs text-slate-400">{ann.dept}</span>
                    </div>
                    <h3 className="text-sm font-bold text-white">{ann.title}</h3>
                    <p className="text-xs text-slate-300 mt-1 leading-relaxed">{ann.summary}</p>
                    <a
                      href={ann.link}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-block mt-2 text-xs font-semibold text-cyan-400 hover:underline"
                    >
                      Official Link & Action →
                    </a>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Feature 338: Shared Resource Library */}
          <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-5 space-y-4">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
              <div>
                <h2 className="text-base font-bold text-white flex items-center gap-2">
                  <span>📚</span> Shared ECE Resource Library (Feature 338)
                </h2>
                <p className="text-xs text-slate-400">Community curated SPICE netlists, Verilog testbenches, and annotated datasheets</p>
              </div>

              <div className="flex gap-2">
                {['ALL', 'SPICE_NETLIST', 'VERILOG_TB', 'MATLAB_SCRIPT', 'DATASHEET'].map(cat => (
                  <button
                    key={cat}
                    onClick={() => setResourceCategory(cat)}
                    className={`px-3 py-1 rounded-lg text-xs font-semibold transition ${
                      resourceCategory === cat
                        ? 'bg-cyan-500 text-slate-950 font-bold'
                        : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
                    }`}
                  >
                    {cat.replace('_', ' ')}
                  </button>
                ))}
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {filteredResources.map(res => (
                <div key={res.id} className="bg-slate-800/60 border border-slate-700/60 rounded-xl p-4 flex flex-col justify-between">
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <span className="px-2 py-0.5 text-[11px] font-bold rounded bg-purple-500/20 text-purple-300 border border-purple-500/30">
                        {res.category}
                      </span>
                      <span className="text-xs font-semibold text-cyan-400">{res.subject}</span>
                    </div>
                    <h3 className="text-sm font-bold text-white mb-1">{res.title}</h3>
                    <div className="text-xs text-slate-400">Uploaded by {res.author}</div>
                  </div>

                  <div className="flex items-center justify-between mt-4 pt-3 border-t border-slate-700/50 text-xs">
                    <span className="text-slate-400">📥 {res.downloads} downloads</span>
                    <div className="flex items-center gap-3">
                      <button
                        onClick={() => handleUpvoteResource(res.id)}
                        className="px-2.5 py-1 bg-slate-700 hover:bg-slate-600 rounded text-cyan-300 font-bold transition"
                      >
                        ▲ {res.upvotes}
                      </button>
                      <a
                        href={res.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="px-3 py-1 bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold rounded transition"
                      >
                        Download
                      </a>
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
