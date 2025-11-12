import { useAuth } from "../context/AuthContext";
import { useNavigate } from "react-router-dom";
import { useState, useEffect, useRef } from "react";
import API from "../services/api";
import html2canvas from "html2canvas";
import jsPDF from "jspdf";

const DashboardHOD = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const [timetable, setTimetable] = useState([]);
  const [filteredTimetable, setFilteredTimetable] = useState([]);
  const [loading, setLoading] = useState(false);

  const [facultyList, setFacultyList] = useState([]);
  const [sectionList, setSectionList] = useState([]);
  const [semesterList, setSemesterList] = useState([]);

  const [selectedFaculty, setSelectedFaculty] = useState("");
  const [selectedSection, setSelectedSection] = useState("");
  const [selectedSemester, setSelectedSemester] = useState("");

  const tableRef = useRef();

  const handleLogout = () => {
    logout();
    navigate("/");
  };

  // 🔹 Fetch Timetable
  const handleViewTimetable = async () => {
    setLoading(true);
    try {
      const res = await API.get("/timetable/list");
      const data = res.data.data || [];

      setTimetable(data);
      setFilteredTimetable(data);

      setSectionList([...new Set(data.map((r) => r.section))]);
      setFacultyList([...new Set(data.map((r) => r.faculty))]);
      setSemesterList([...new Set(data.map((r) => r.year))]);
    } catch (err) {
      alert(err.response?.data?.detail || "Unable to fetch timetable");
      setTimetable([]);
      setFilteredTimetable([]);
    } finally {
      setLoading(false);
    }
  };

  // 🔹 Filter Logic
  useEffect(() => {
    let filtered = timetable;

    if (selectedFaculty)
      filtered = filtered.filter((t) => t.faculty === selectedFaculty);
    if (selectedSection)
      filtered = filtered.filter((t) => t.section === selectedSection);
    if (selectedSemester)
      filtered = filtered.filter((t) => String(t.year) === String(selectedSemester));

    setFilteredTimetable(filtered);
  }, [selectedFaculty, selectedSection, selectedSemester, timetable]);

  const days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];
  const timeSlots = [
    "9:00–10:00",
    "10:00–11:00",
    "11:00–12:00",
    "12:00–1:00",
    "1:00–2:00",
    "2:00–3:00",
    "3:00–4:00",
  ];

const downloadPDF = async () => {
  const input = tableRef.current;
  if (!input) return;

  // Clone timetable node
  const clone = input.cloneNode(true);
  document.body.appendChild(clone);
  clone.style.position = "absolute";
  clone.style.left = "-9999px";
  clone.style.background = "#ffffff";

  // ✅ Sanitize OKLCH / LAB colors (replace with RGB)
  const sanitizeColors = (el) => {
    const computedStyle = window.getComputedStyle(el);
    for (const prop of ["color", "backgroundColor", "borderColor"]) {
      const val = computedStyle[prop];
      if (val && val.includes("oklch")) {
        // Replace any OKLCH-based color with neutral RGB
        el.style[prop] = "#f8fafc"; // Tailwind neutral background
      }
    }
    for (const child of el.children) sanitizeColors(child);
  };
  sanitizeColors(clone);

  // ✅ Inject fallback CSS to avoid re-triggering Tailwind dynamic colors
  const style = document.createElement("style");
  style.innerHTML = `
    * {
      font-family: 'Inter', sans-serif !important;
      color: #111827 !important;
    }
    table { border-collapse: collapse !important; width: 100% !important; }
    th, td {
      border: 1px solid #000 !important;
      text-align: center !important;
      padding: 6px !important;
    }
    th { background: rgb(219, 234, 254) !important; }
    td:first-child { background: rgb(224, 242, 254) !important; font-weight: 600 !important; }
    tr:nth-child(even) td:not(:first-child) { background: rgb(236, 253, 245) !important; }
    .lunch-cell { background: rgb(255, 247, 204) !important; font-weight: bold !important; }
  `;
  clone.prepend(style);

  try {
    const canvas = await html2canvas(clone, {
      scale: 3,
      backgroundColor: "#ffffff",
      logging: false,
      useCORS: true,
    });

    document.body.removeChild(clone);

    const pdf = new jsPDF("landscape", "mm", "a4");
    const pageWidth = pdf.internal.pageSize.getWidth();
    const pageHeight = pdf.internal.pageSize.getHeight();

    const imgData = canvas.toDataURL("image/png");
    const aspectRatio = canvas.width / canvas.height;
    let imgWidth = pageWidth - 10;
    let imgHeight = imgWidth / aspectRatio;
    if (imgHeight > pageHeight - 45) {
      imgHeight = pageHeight - 45;
      imgWidth = imgHeight * aspectRatio;
    }

    const x = (pageWidth - imgWidth) / 2;
    const y = 45;

    pdf.setFont("helvetica", "bold");
    pdf.setFontSize(14);
    pdf.text("MORADABAD INSTITUTE OF TECHNOLOGY, MORADABAD", pageWidth / 2, 15, { align: "center" });
    pdf.setFont("helvetica", "normal");
    pdf.setFontSize(12);
    pdf.text("Department of Computer Science & Engineering - Timetable", pageWidth / 2, 22, { align: "center" });

    const studentName = user?.name || "Student";
    const sem = semester || "N/A";
    const sec = section || "N/A";
    const academicYear = "2025–26";

    pdf.setFontSize(11);
    pdf.text(`Student: ${studentName}   |   Semester: ${sem}   |   Section: ${sec}   |   Academic Year: ${academicYear}`, pageWidth / 2, 30, { align: "center" });

    pdf.addImage(imgData, "PNG", x, y, imgWidth, imgHeight);
    const date = new Date().toLocaleDateString("en-IN", { day: "2-digit", month: "short", year: "numeric" });
    pdf.setFontSize(10);
    pdf.setTextColor(90);
    pdf.text(`Generated by EduChrono on ${date}`, pageWidth / 2, pageHeight - 8, { align: "center" });

    pdf.save(`Timetable_${studentName}.pdf`);
  } catch (err) {
    console.error("PDF Error:", err);
    alert("Error generating PDF.");
  }
};

  return (
    <div className="p-8 bg-gray-50 min-h-screen">
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-semibold text-blue-700">
          HOD Dashboard – {user?.name}
        </h1>
        <button
          onClick={handleLogout}
          className="bg-red-500 text-white px-4 py-2 rounded-md hover:bg-red-600"
        >
          Logout
        </button>
      </div>

      {/* Timetable Section */}
      <div className="bg-white shadow rounded-xl p-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-lg font-medium">📅 Department Timetable</h2>
          {filteredTimetable.length > 0 && (
            <button
              onClick={downloadPDF}
              className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition"
            >
              📄 Download PDF
            </button>
          )}
        </div>

        <div className="flex flex-wrap gap-4 mb-4">
          <button
            onClick={handleViewTimetable}
            className="bg-green-600 hover:bg-green-700 text-white px-5 py-2 rounded-md"
          >
            Load Timetable
          </button>

          {timetable.length > 0 && (
            <>
              <select
                value={selectedFaculty}
                onChange={(e) => setSelectedFaculty(e.target.value)}
                className="border px-3 py-2 rounded-md text-gray-700"
              >
                <option value="">All Faculty</option>
                {facultyList.map((f, i) => (
                  <option key={i} value={f}>
                    {f}
                  </option>
                ))}
              </select>

              <select
                value={selectedSection}
                onChange={(e) => setSelectedSection(e.target.value)}
                className="border px-3 py-2 rounded-md text-gray-700"
              >
                <option value="">All Sections</option>
                {sectionList.map((s, i) => (
                  <option key={i} value={s}>
                    {s}
                  </option>
                ))}
              </select>

              <select
                value={selectedSemester}
                onChange={(e) => setSelectedSemester(e.target.value)}
                className="border px-3 py-2 rounded-md text-gray-700"
              >
                <option value="">All Semesters</option>
                {semesterList.map((sem, i) => (
                  <option key={i} value={sem}>
                    Semester {sem}
                  </option>
                ))}
              </select>
            </>
          )}
        </div>

        {loading && <p className="text-gray-500">Loading timetable...</p>}

        {!loading && filteredTimetable.length > 0 && (
          <div ref={tableRef} className="overflow-x-auto mt-6">
            <table className="border-collapse border border-gray-400 w-full text-center">
              <thead className="bg-green-100">
                <tr>
                  <th className="border border-gray-400 p-2 w-28">Day</th>
                  {timeSlots.map((slot) => (
                    <th
                      key={slot}
                      className="border border-gray-400 p-2 text-sm font-semibold text-gray-700"
                    >
                      {slot}
                    </th>
                  ))}
                </tr>
              </thead>

              <tbody>
                {days.map((day, dayIndex) => (
                  <tr key={day}>
                    <td className="border border-gray-400 p-2 font-semibold bg-gray-50">
                      {day}
                    </td>

                    {timeSlots.map((slot, slotIndex) => {
                      if (slot === "1:00–2:00") {
                        if (dayIndex === 0)
                          return (
                            <td
                              key="lunch"
                              rowSpan={days.length}
                              className="border border-gray-400 bg-yellow-100 font-semibold text-gray-800 text-center align-middle"
                            >
                              🍱 LUNCH BREAK
                            </td>
                          );
                        return null;
                      }

                      // 🧩 Handle Labs (2-hour span)
                      const lab = filteredTimetable.find(
                        (t) =>
                          t.day?.toLowerCase() === day.toLowerCase() &&
                          t.type === "P" &&
                          t.time_slot?.startsWith(slot)
                      );

                      const prevLab = filteredTimetable.find(
                        (t) =>
                          t.day?.toLowerCase() === day.toLowerCase() &&
                          t.type === "P" &&
                          t.time_slot?.includes(slot) &&
                          !t.time_slot?.startsWith(slot)
                      );
                      if (prevLab) return null;

                      if (lab) {
                        const sameLab = filteredTimetable.filter(
                          (l) =>
                            l.day?.toLowerCase() === day.toLowerCase() &&
                            l.subject === lab.subject &&
                            l.time_slot === lab.time_slot
                        );
                        const mergedRooms = sameLab
                          .map(
                            (l) =>
                              `${l.room}${l.batch ? ` (${l.batch})` : ""}`
                          )
                          .join(" | ");

                        return (
                          <td
                            key={`${day}-${slot}-lab`}
                            colSpan={2}
                            className="border border-gray-400 bg-green-50 font-semibold text-sm text-gray-800 p-2 whitespace-pre-line"
                          >
                            🧪 {lab.subject}
                            <br />
                            {mergedRooms}
                            <br />
                            {lab.faculty}
                            <br />
                            Sec {lab.section} | Sem {lab.year}
                          </td>
                        );
                      }

                      // 🧩 Lecture / Tutorial slots
                      const slotEntries = filteredTimetable.filter(
                        (t) =>
                          t.day?.toLowerCase() === day.toLowerCase() &&
                          t.time_slot?.toLowerCase() === slot.toLowerCase()
                      );

                      if (slotEntries.length === 0)
                        return (
                          <td
                            key={`${day}-${slot}`}
                            className="border border-gray-400 p-2 text-sm text-gray-700"
                          >
                            -
                          </td>
                        );

                      // Split B1/B2 for T
                      let finalEntries = [];
                      slotEntries.forEach((e) => {
                        if (e.type === "T") {
                          if (e.batch) finalEntries.push(e);
                          else {
                            finalEntries.push({ ...e, batch: "B1" });
                            finalEntries.push({ ...e, batch: "B2" });
                          }
                        } else finalEntries.push(e);
                      });

                      return (
                        <td
                          key={`${day}-${slot}`}
                          className="border border-gray-400 p-2 whitespace-pre-line text-sm font-medium text-gray-800"
                        >
                          {finalEntries.map((entry, idx) => {
                            const bgClass =
                              entry.type === "P"
                                ? "bg-green-50"
                                : entry.type === "T"
                                ? "bg-blue-50"
                                : "bg-white";

                            return (
                              <div
                                key={idx}
                                className={`mb-1 border-b border-gray-300 pb-1 last:border-0 rounded-md p-1 ${bgClass}`}
                              >
                                <span className="block font-semibold text-gray-900">
                                  {entry.subject} ({entry.type}
                                  {entry.batch ? ` - ${entry.batch}` : ""})
                                </span>
                                <span className="block text-gray-700">
                                  {entry.room}
                                </span>
                                <span className="block text-gray-700">
                                  {entry.faculty}
                                </span>
                                <span className="block text-gray-500">
                                  Sec {entry.section} | Sem {entry.year}
                                </span>
                              </div>
                            );
                          })}
                        </td>
                      );
                    })}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {!loading && filteredTimetable.length === 0 && (
          <p className="text-gray-500 mt-4">No timetable data available yet.</p>
        )}
      </div>
    </div>
  );
};

export default DashboardHOD;
