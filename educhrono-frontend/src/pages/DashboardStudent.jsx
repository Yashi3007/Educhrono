import { useEffect, useState, useRef } from "react";
import { useAuth } from "../context/AuthContext";
import { useNavigate } from "react-router-dom";
import API from "../services/api";
import html2canvas from "html2canvas";
import jsPDF from "jspdf";
import TimetableTable from "../components/TimetableTable";   // ✅ Use SAME universal table
import { normalizeStudentTimetable } from "../utils/TimetableNormalizer";

const DashboardStudent = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const [timetable, setTimetable] = useState([]);
  const [semester, setSemester] = useState("");
  const [section, setSection] = useState("");
  const [loading, setLoading] = useState(false);

  const tableRef = useRef();

  const handleLogout = () => {
    logout();
    navigate("/");
  };

  useEffect(() => {
    if (user?.semester && user?.section) {
      fetchTimetable(user.semester, user.section);
    }
  }, [user]);

  const fetchTimetable = async (semester, section) => {
    try {
      setLoading(true);
      const res = await API.get(`/timetable/student/${semester}/${section}`);

      const normalized = normalizeStudentTimetable(res.data.timetable);

      // Normalize time formats like admin/hod
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

      const mapped = normalized.map((i) => ({
        ...i,
        time_slot: mapSlot[i.time_slot] || i.time_slot,
        slot2: mapSlot[i.slot2] || i.slot2,
      }));

      setTimetable(mapped);
      setSemester(res.data.semester);
      setSection(res.data.section);
    } catch (err) {
      console.error("Student timetable error:", err);
      setTimetable([]);
    } finally {
      setLoading(false);
    }
  };

  // PDF generation stays unchanged

  const downloadPDF = async () => {
    const input = tableRef.current;
    if (!input) return;

    // Clone for clean PDF rendering
    const clone = input.cloneNode(true);
    document.body.appendChild(clone);
    clone.style.position = "absolute";
    clone.style.left = "-9999px";
    clone.style.background = "#ffffff";

    // Sanitize Tailwind OKLCH colors
    const sanitizeColors = (el) => {
      const computed = window.getComputedStyle(el);
      ["color", "backgroundColor", "borderColor"].forEach((prop) => {
        const val = computed[prop];
        if (val && val.includes("oklch")) el.style[prop] = "#f8fafc";
      });
      for (const c of el.children) sanitizeColors(c);
    };
    sanitizeColors(clone);

    // Fix table border/colors for PDF
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

      const reservedSpace = 40; // Space for header + signatures
      if (imgHeight > pageHeight - reservedSpace - 35) {
        imgHeight = pageHeight - reservedSpace - 35;
        imgWidth = imgHeight * aspectRatio;
      }

      const x = (pageWidth - imgWidth) / 2;
      const y = 40;

      // HEADER
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
        "Department of Computer Science & Engineering – Student Timetable (9:00 AM – 5:00 PM)",
        pageWidth / 2,
        22,
        { align: "center" }
      );

      const studentName = user?.name || "Student";
      const academicYear = "2025–26";

      pdf.setFontSize(11);
      pdf.text(
        `Student: ${studentName}   |   Semester: ${semester}   |   Section: ${section}   |   Academic Year: ${academicYear}`,
        pageWidth / 2,
        30,
        { align: "center" }
      );

      // Add table screenshot
      pdf.addImage(imgData, "PNG", x, y, imgWidth, imgHeight);

      // FOOTER SIGNATURES
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

      pdf.save(`Student_Timetable_${studentName}.pdf`);
    } catch (err) {
      console.error("PDF Error:", err);
      alert("Error generating PDF.");
    }
  };

  const days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];
  const timeSlots = [
    "9:00–10:00",
    "10:00–11:00",
    "11:00–12:00",
    "12:00–1:00",
    "1:00–2:00",
    "2:00–3:00",
    "3:00–4:00",
    "4:00–5:00"
  ];

  return (
    <div className="p-8 bg-gray-50 min-h-screen">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-semibold text-blue-700">
            Student Dashboard – {user?.name}
          </h1>

          {(semester || section) && (
            <p className="text-gray-600 mt-1">
              🎓 Semester: <b>{semester}</b> | 📘 Section: <b>{section}</b>
            </p>
          )}
        </div>

        <button
          onClick={handleLogout}
          className="bg-red-500 text-white px-4 py-2 rounded-md hover:bg-red-600"
        >
          Logout
        </button>
      </div>

      <div className="bg-white shadow rounded-xl p-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-lg font-medium text-gray-800">📘 My Class Timetable</h2>
          {timetable.length > 0 && (
            <button
              onClick={downloadPDF}
              className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
            >
              📄 Download PDF
            </button>
          )}
        </div>

        {loading && <p>Loading...</p>}

        {!loading && timetable.length > 0 && (
          <div ref={tableRef} className="overflow-x-auto mt-6">
            <TimetableTable
              timetable={timetable}
              days={days}
              timeSlots={timeSlots}
            />
          </div>
        )}
      </div>
    </div>
  );
};

export default DashboardStudent;
