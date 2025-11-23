import { useAuth } from "../context/AuthContext";
import { useNavigate } from "react-router-dom";
import { useEffect, useState, useRef } from "react";
import API from "../services/api";
import html2canvas from "html2canvas";
import jsPDF from "jspdf";
import TimetableTable from "../components/TimetableTable";

const DashboardFaculty = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [timetable, setTimetable] = useState([]);
  const [filteredTimetable, setFilteredTimetable] = useState([]);
  const [loading, setLoading] = useState(false);
  const [sectionList, setSectionList] = useState([]);
  const [semesterList, setSemesterList] = useState([]);
  const [selectedSection, setSelectedSection] = useState("");
  const [selectedSemester, setSelectedSemester] = useState("");
  const tableRef = useRef();

  const handleLogout = () => {
    logout();
    navigate("/");
  };

  // --------------------------------------------------------
  // FETCH FACULTY TIMETABLE (APPLY SLOT2 + GROUP EXPANSION)
  // --------------------------------------------------------
  const fetchTimetable = async () => {
    if (!user?.name) return;
    try {
      setLoading(true);
      const res = await API.get(`/timetable/faculty/${user.name}`);
      let data = res.data.timetable || [];

      // -------------------------------
      // STEP 1: Expand Groups (A1/A2)
      // -------------------------------
      let expanded = [];

      data.forEach((item) => {
        if (item.Groups && Array.isArray(item.Groups)) {
          item.Groups.forEach((g) => {
            expanded.push({
              faculty: g.faculty?.trim() || "",
              subject: g.subject?.trim() || "",
              section: g.group?.trim() || "",
              day: item.Day?.trim() || "",
              time_slot: item.Slot?.trim() || "",
              slot2: item.Slot2?.trim() || null,
              room: g.room || "",
              type: item.Type || "",
              year: item.Semester,
              isGroupSplit: true,
            });
          });
        } else {
          expanded.push({
            faculty: item.Faculty?.trim() || "",
            subject: item.Subject?.trim() || "",
            section: item.Section?.trim() || "",
            day: item.Day?.trim() || "",
            time_slot: item.Slot?.trim() || "",
            slot2: item.Slot2?.trim() || null,
            room: item.Room || "",
            type: item.Type || "",
            year: item.Semester,
          });
        }
      });

      // -------------------------------
      // STEP 2: Normalize SLOT + SLOT2
      // -------------------------------
      const mapSlot = {
        "09:00-10:00": "9:00–10:00",
        "10:00-11:00": "10:00–11:00",
        "11:00-12:00": "11:00–12:00",
        "12:00-13:00": "12:00–1:00",
        "13:00-14:00": "1:00–2:00",
        "14:00-15:00": "2:00–3:00",
        "15:00-16:00": "3:00–4:00",
        "16:00-17:00": "4:00–5:00",
      };

      expanded = expanded.map((i) => ({
        ...i,
        time_slot: mapSlot[i.time_slot] || i.time_slot,
        slot2: i.slot2 ? mapSlot[i.slot2] || i.slot2 : null,
      }));

      // Save to state
      setTimetable(expanded);
      setFilteredTimetable(expanded);

      setSectionList([...new Set(expanded.map((t) => t.section))]);
      setSemesterList([...new Set(expanded.map((t) => t.year))]);
    } catch (err) {
      console.error("Error fetching timetable:", err);
      setTimetable([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTimetable();
  }, [user]);

  // FILTERS
  useEffect(() => {
    let filtered = timetable;
    if (selectedSection)
      filtered = filtered.filter((t) => t.section === selectedSection);
    if (selectedSemester)
      filtered = filtered.filter(
        (t) => String(t.year) === String(selectedSemester)
      );
    setFilteredTimetable(filtered);
  }, [selectedSection, selectedSemester, timetable]);

  // --------------------------------------------------------
  // PDF EXPORT
  // --------------------------------------------------------
  const downloadPDF = async () => {
    const input = tableRef.current;
    if (!input) return;

    const clone = input.cloneNode(true);
    document.body.appendChild(clone);
    clone.style.position = "absolute";
    clone.style.left = "-9999px";
    clone.style.background = "#ffffff";

    const sanitizeColors = (el) => {
      const computed = window.getComputedStyle(el);
      for (const prop of ["color", "backgroundColor", "borderColor"]) {
        const val = computed[prop];
        if (val && val.includes("oklch")) el.style[prop] = "#f8fafc";
      }
      for (const child of el.children) sanitizeColors(child);
    };
    sanitizeColors(clone);

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
      let imgWidth = pageWidth - 20;
      let imgHeight = imgWidth / aspectRatio;

      const reservedSpace = 40;
      if (imgHeight > pageHeight - reservedSpace - 35) {
        imgHeight = pageHeight - reservedSpace - 35;
        imgWidth = imgHeight * aspectRatio;
      }

      const x = (pageWidth - imgWidth) / 2;
      const y = 40;

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
        "Department of Computer Science & Engineering – Faculty Timetable (9:00 AM – 5:00 PM)",
        pageWidth / 2,
        22,
        { align: "center" }
      );

      const facultyName = user?.name || "Faculty";
      const academicYear = "2025–26";
      const sem = selectedSemester || "All";
      const sec = selectedSection || "All";

      pdf.setFontSize(11);
      pdf.text(
        `Faculty: ${facultyName}   |   Semester: ${sem}   |   Section: ${sec}   |   Academic Year: ${academicYear}`,
        pageWidth / 2,
        30,
        { align: "center" }
      );

      pdf.addImage(imgData, "PNG", x, y, imgWidth, imgHeight);

      const date = new Date().toLocaleDateString("en-IN", {
        day: "2-digit",
        month: "short",
        year: "numeric",
      });

      const footerY = y + imgHeight + 18;

      pdf.setDrawColor(180);
      pdf.setLineWidth(0.3);
      pdf.line(15, footerY - 10, pageWidth - 15, footerY - 10);

      const leftX = 35;
      const rightX = pageWidth - 105;
      const lineY = footerY - 4;

      pdf.setDrawColor(0);
      pdf.line(leftX, lineY, leftX + 60, lineY);
      pdf.line(rightX, lineY, rightX + 60, lineY);

      pdf.setFont("helvetica", "bold");
      pdf.setFontSize(11);
      pdf.text("(Ms. Neha Gupta)", leftX + 5, footerY + 4);
      pdf.setFont("helvetica", "normal");
      pdf.setFontSize(10);
      pdf.text("Dept. Coordinator (Timetable)", leftX + 5, footerY + 12);

      pdf.setFont("helvetica", "bold");
      pdf.setFontSize(11);
      pdf.text("(Dr. Lalit Mohan Trivedi)", rightX + 5, footerY + 4);
      pdf.setFont("helvetica", "normal");
      pdf.setFontSize(10);
      pdf.text("Convener (Timetable)", rightX + 5, footerY + 12);

      pdf.setFontSize(9);
      pdf.setTextColor(90);
      pdf.text(
        `Generated by EduChrono on ${date}`,
        pageWidth / 2,
        pageHeight - 8,
        { align: "center" }
      );

      pdf.save(`Faculty_Timetable_${facultyName}.pdf`);
    } catch (err) {
      console.error("PDF Error:", err);
      alert("Error generating PDF.");
    }
  };

  return (
    <div className="p-8 bg-gray-50 min-h-screen">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-semibold text-blue-700">
          Faculty Dashboard – {user?.name}
        </h1>
        <button
          onClick={handleLogout}
          className="bg-red-500 text-white px-4 py-2 rounded-md hover:bg-red-600"
        >
          Logout
        </button>
      </div>

      <div className="bg-white shadow rounded-xl p-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-lg font-medium text-gray-800">
            📅 My Teaching Schedule
          </h2>
          {filteredTimetable.length > 0 && (
            <button
              onClick={downloadPDF}
              className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
            >
              📄 Download PDF
            </button>
          )}
        </div>

        <div className="flex flex-wrap gap-4 mb-4">
          {timetable.length > 0 && (
            <>
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
            <TimetableTable
              timetable={filteredTimetable}
              days={[
                "Monday",
                "Tuesday",
                "Wednesday",
                "Thursday",
                "Friday",
                "Saturday",
              ]}
              timeSlots={[
                "9:00–10:00",
                "10:00–11:00",
                "11:00–12:00",
                "12:00–1:00",
                "1:00–2:00",
                "2:00–3:00",
                "3:00–4:00",
                "4:00–5:00",
              ]}
            />
          </div>
        )}
      </div>
    </div>
  );
};

export default DashboardFaculty;
