// utils/TimetableNormalizer.js

export const normalizeStudentTimetable = (raw) => {
  if (!raw) return [];

  const result = [];

  raw.forEach((item) => {
    const base = {
      day: item.Day,
      time_slot: item.Slot,
      slot2: item.Slot2 || null,
      year: item.Semester,
      type: item.Type,
      section: item.Section,
    };

    // ---------------------------------------
    // 1️⃣ GROUP-SPLIT T/P BLOCKS
    // ---------------------------------------
    if (Array.isArray(item.Groups) && item.Groups.length > 0) {
      item.Groups.forEach((g) => {
        result.push({
          ...base,
          isGroupSplit: true,
          subject: g.subject,
          faculty: g.faculty,
          room: g.room,
          type: g.type || item.Type,       // ensure P/T
          section: g.group,                // A1, A2
        });
      });
      return;
    }

    // ---------------------------------------
    // 2️⃣ NORMAL ENTRIES (L, PDP, COE)
    // ---------------------------------------
    result.push({
      ...base,
      subject: item.Subject,
      faculty: item.Faculty,
      room: item.Room,
    });
  });

  return result;
};
