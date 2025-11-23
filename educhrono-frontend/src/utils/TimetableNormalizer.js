// utils/TimetableNormalizer.js

export const normalizeStudentTimetable = (raw) => {
  if (!raw) return [];

  const result = [];

  raw.forEach((item) => {
    const base = {
      day: item.Day,
      time_slot: item.Slot,
      slot2: item.Slot2 || null,
      section: item.Section,
      year: item.Semester,
      type: item.Type,
    };

    // -------------------------------
    // CASE 1: Grouped T / P blocks
    // -------------------------------
    if (item.Groups && Array.isArray(item.Groups)) {
      item.Groups.forEach((g) => {
        result.push({
          ...base,
          isGroupSplit: true,
          subject: g.subject,
          faculty: g.faculty,
          room: g.room,
          type: g.type,       // override T/P
          section: `${item.Section}-${g.group}`,  // e.g., A-A1 / A-A2
        });
      });
      return;
    }

    // -------------------------------
    // CASE 2: Normal lectures (L) & COE/PDP
    // -------------------------------
    result.push({
      ...base,
      subject: item.Subject,
      faculty: item.Faculty,
      room: item.Room,
    });
  });

  return result;
};
