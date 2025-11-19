import { useAuth } from "../context/AuthContext";
import { useNavigate } from "react-router-dom";
import { useState, useEffect, useRef } from "react";
import API from "../services/api";
import html2canvas from "html2canvas";
import jsPDF from "jspdf";
import TimetableTable from "../components/TimetableTable";
import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from "recharts";

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
  const [workloadData, setWorkloadData] = useState([]);
  const [classTypeCounts, setClassTypeCounts] = useState({
    L: 0,
    T: 0,
    P: 0,
    COE: 0,
    PDP: 0,
  });

  const tableRef = useRef();

  const handleLogout = () => {
    logout();
    navigate("/");
  };

  // 🔹 Fetch timetable automatically
  const handleViewTimetable = async () => {
    setLoading(true);
    try {
      const res = await API.get("/timetable/list");
      let data = res.data.data || [];

      data = data.map((r) => ({
        ...r,
        faculty: r.faculty?.trim(),
        section: r.section?.trim()?.toUpperCase()?.replace(/\s*\(B\d\)/gi, ""),
        day: r.day?.trim(),
        time_slot: r.time_slot?.trim(),
      }));

      setTimetable(data);
      setFilteredTimetable(data);
      setFacultyList([...new Set(data.map((r) => r.faculty).filter(Boolean))]);
      setSectionList([...new Set(data.map((r) => r.section).filter(Boolean))]);
      setSemesterList([...new Set(data.map((r) => r.year).filter(Boolean))]);
    } catch (err) {
      console.error("Timetable fetch error:", err);
      setTimetable([]);
      setFilteredTimetable([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    handleViewTimetable();
  }, []);

  // 🔹 Filtering logic
  useEffect(() => {
    let filtered = timetable;

    if (selectedFaculty)
      filtered = filtered.filter(
        (t) =>
          t.faculty?.toLowerCase().trim() ===
          selectedFaculty.toLowerCase().trim()
      );

    if (selectedSection)
      filtered = filtered.filter(
        (t) =>
          t.section?.replace(/\s+/g, "").toUpperCase() ===
          selectedSection.replace(/\s+/g, "").toUpperCase()
      );

    if (selectedSemester)
      filtered = filtered.filter(
        (t) =>
          String(t.year).replace(/\D/g, "") ===
          String(selectedSemester).replace(/\D/g, "")
      );

    setFilteredTimetable(filtered);
  }, [selectedFaculty, selectedSection, selectedSemester, timetable]);

  // 🧾 PDF Download
const downloadPDF = async () => {
  const input = tableRef.current;
  if (!input) return;

  // Clone table to clean render
  const clone = input.cloneNode(true);
  document.body.appendChild(clone);
  clone.style.position = "absolute";
  clone.style.left = "-9999px";
  clone.style.background = "#ffffff";

  // Sanitize Tailwind oklch() colors
  const sanitizeColors = (el) => {
    const computed = window.getComputedStyle(el);
    for (const prop of ["color", "backgroundColor", "borderColor"]) {
      const val = computed[prop];
      if (val && val.includes("oklch")) el.style[prop] = "#f8fafc";
    }
    for (const child of el.children) sanitizeColors(child);
  };
  sanitizeColors(clone);

  // Clean table styling
  const style = document.createElement("style");
  style.innerHTML = `
    * { font-family: 'Inter', sans-serif !important; color: #111827 !important; }
    table { border-collapse: collapse !important; width: 100% !important; }
    th, td { border: 1px solid #000 !important; padding: 6px !important; text-align: center !important; }
    th { background: rgb(219,234,254) !important; }
    td:first-child { background: rgb(224,242,254) !important; font-weight: 600 !important; }
    .lunch-cell { background: rgb(255,247,204) !important; font-weight: bold !important; }
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

    // Adjust for 9–5 timetable
    let imgWidth = pageWidth - 20;
    let imgHeight = imgWidth / aspectRatio;
    if (imgHeight > pageHeight - 60) {
      imgHeight = pageHeight - 60;
      imgWidth = imgHeight * aspectRatio;
    }

    const x = (pageWidth - imgWidth) / 2;
    const y = 40;

    // Header
    pdf.setFont("helvetica", "bold");
    pdf.setFontSize(14);
    pdf.text(
      "MORADABAD INSTITUTE OF TECHNOLOGY, MORADABAD",
      pageWidth / 2,
      15,
      { align: "center" }
    );

    pdf.setFont("helvetica", "normal");
    pdf.setFontSize(12);
    pdf.text(
      "Department of Computer Science & Engineering – Consolidated Timetable (9:00 AM – 5:00 PM)",
      pageWidth / 2,
      22,
      { align: "center" }
    );

    const name = user?.name || "HOD";
    const sem = selectedSemester || "All";
    const sec = selectedSection || "All";
    const academicYear = "2025–26";

    pdf.setFontSize(11);
    pdf.text(
      `Generated by: ${name} | Semester: ${sem} | Section: ${sec} | Academic Year: ${academicYear}`,
      pageWidth / 2,
      30,
      { align: "center" }
    );

    // Add timetable image
    pdf.addImage(imgData, "PNG", x, y, imgWidth, imgHeight);

    const date = new Date().toLocaleDateString("en-IN", {
      day: "2-digit",
      month: "short",
      year: "numeric",
    });

    pdf.setFontSize(10);
    pdf.setTextColor(90);
    let footerY = y + imgHeight + 25;
    if (footerY > pageHeight - 25) {
      pdf.addPage();
      footerY = 25;
    }

    // Divider line
    pdf.setDrawColor(180);
    pdf.setLineWidth(0.3);
    pdf.line(15, footerY - 10, pageWidth - 15, footerY - 10);

    // --- Signatures (Neat Alignment) ---
    const leftX = 35;
    const rightX = pageWidth - 105;
    const lineY = footerY - 4;

    // Signature lines
    pdf.setDrawColor(0);
    pdf.line(leftX, lineY, leftX + 60, lineY);
    pdf.line(rightX, lineY, rightX + 60, lineY);

    // Left Signature
    pdf.setFont("helvetica", "bold");
    pdf.setFontSize(11);
    pdf.text("(Ms. Neha Gupta)", leftX + 5, footerY + 4);
    pdf.setFont("helvetica", "normal");
    pdf.setFontSize(10);
    pdf.text("Dept. Coordinator (Timetable)", leftX + 5, footerY + 12);

    // Right Signature
    pdf.setFont("helvetica", "bold");
    pdf.setFontSize(11);
    pdf.text("(Dr. Lalit Mohan Trivedi)", rightX + 5, footerY + 4);
    pdf.setFont("helvetica", "normal");
    pdf.setFontSize(10);
    pdf.text("Convener (Timetable)", rightX + 5, footerY + 12);

    // Footer Info
    pdf.setFontSize(9);
    pdf.setTextColor(90);
    pdf.text(
      `Generated by EduChrono on ${date}`,
      pageWidth / 2,
      pageHeight - 10,
      { align: "center" }
    );

    // Save File
    pdf.save(`HOD_Timetable_${name}.pdf`);
  } catch (err) {
    console.error("PDF Error:", err);
    alert("Error generating PDF.");
  }
};


  // 🔹 Auto-update workload on filter change
  useEffect(() => {
    const dataSource = filteredTimetable.length ? filteredTimetable : timetable;

    if (!dataSource.length) {
      setWorkloadData([]);
      setClassTypeCounts({ L: 0, T: 0, P: 0, COE: 0, PDP: 0 });
      return;
    }

    // Faculty workload
    const facultyCounts = {};
    dataSource.forEach((t) => {
      if (t.faculty) {
        const name = t.faculty.trim();
        facultyCounts[name] = (facultyCounts[name] || 0) + 1;
      }
    });

    const totalSessions = Object.values(facultyCounts).reduce((a, b) => a + b, 0);
    const workload = Object.entries(facultyCounts).map(([name, count]) => ({
      name,
      value: parseFloat(((count / totalSessions) * 100).toFixed(1)),
    }));

    setWorkloadData(workload);

    // Class type counts
    const typeCounts = { L: 0, T: 0, P: 0, COE: 0, PDP: 0 };
    dataSource.forEach((t) => {
      const type = t.type?.toUpperCase();
      if (typeCounts[type] !== undefined) typeCounts[type]++;
    });
    setClassTypeCounts(typeCounts);
  }, [filteredTimetable]);

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
          <h2 className="text-lg font-medium text-gray-800">
            📘 Department Timetable
          </h2>
          {filteredTimetable.length > 0 && (
            <button
              onClick={downloadPDF}
              className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition"
            >
              📄 Download PDF
            </button>
          )}
        </div>

        {/* Filters */}
        {timetable.length > 0 && (
          <div className="flex flex-wrap gap-4 mb-4">
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
          </div>
        )}

        {/* Timetable */}
        {loading && <p className="text-gray-500">Loading timetable...</p>}
        {!loading && filteredTimetable.length > 0 && (
          <div ref={tableRef} className="overflow-x-auto mt-6">
            <TimetableTable
              timetable={filteredTimetable}
              days={["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]}
              timeSlots={[
                "9:00–10:00",
                "10:00–11:00",
                "11:00–12:00",
                "12:00–1:00",
                "1:00–2:00",
                "2:00–3:00",
                "3:00–4:00",
                "4:00-5:00"
              ]}
            />
          </div>
        )}
        {!loading && filteredTimetable.length === 0 && (
          <p className="text-gray-500 mt-4 text-center">
            No timetable data available yet.
          </p>
        )}

        {/* Workload Chart (Always Visible) */}
        {workloadData.length > 0 && (
          <div className="bg-white mt-8 p-6 rounded-xl shadow-md">
            <h3 className="text-lg font-semibold text-gray-800 mb-2">
              Faculty Workload Distribution (%)
            </h3>
            <p className="text-sm text-gray-600 mb-4">
              Class Counts — L: <b>{classTypeCounts.L}</b>, T: <b>{classTypeCounts.T}</b>, 
              P: <b>{classTypeCounts.P}</b>, COE: <b>{classTypeCounts.COE}</b>, PDP:{" "}
              <b>{classTypeCounts.PDP}</b>
            </p>

            <ResponsiveContainer width="100%" height={400}>
              <PieChart>
                <Pie
                  data={workloadData}
                  dataKey="value"
                  nameKey="name"
                  cx="50%"
                  cy="50%"
                  outerRadius={140}
                  fill="#8884d8"
                  label={({ name, value }) => `${name}: ${value}%`}
                >
                  {workloadData.map((_, index) => (
                    <Cell
                      key={`cell-${index}`}
                      fill={`hsl(${(index * 60) % 360}, 70%, 60%)`}
                    />
                  ))}
                </Pie>
                <Tooltip />
                <Legend layout="vertical" align="right" verticalAlign="middle" />
              </PieChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>
    </div>
  );
};

export default DashboardHOD;
