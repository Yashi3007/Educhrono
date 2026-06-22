// ----------------------------------------------
// FIXED DashboardTimetable.jsx  (Admin Timetable)
// ----------------------------------------------

import { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import FileUploader from "../components/FileUploader";
import API from "../services/api";
import html2canvas from "html2canvas";
import jsPDF from "jspdf";
import TimetableTable from "../components/TimetableTable";

// ----------------------------------------------
// SinglePaginationComponent
// ----------------------------------------------
function SinglePaginationComponent({ data }) {
  const [page, setPage] = useState(1);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [search, setSearch] = useState("");

  const filtered = data.filter((row) =>
    JSON.stringify(row).toLowerCase().includes(search.toLowerCase())
  );

  const totalPages = Math.ceil(filtered.length / rowsPerPage);

  const paginated = filtered.slice(
    (page - 1) * rowsPerPage,
    page * rowsPerPage
  );

  return (
    <>
      {/* Search + Rows selector */}
      <div className="flex justify-between items-center mb-3">
        <input
          type="text"
          placeholder="Search..."
          className="border px-3 py-2 rounded-md text-sm w-1/3"
          value={search}
          onChange={(e) => {
            setSearch(e.target.value);
            setPage(1);
          }}
        />

        <select
          value={rowsPerPage}
          onChange={(e) => {
            setRowsPerPage(Number(e.target.value));
            setPage(1);
          }}
          className="border px-3 py-2 rounded-md text-sm"
        >
          {[5, 10, 20, 50, 100].map((n) => (
            <option key={n} value={n}>
              {n} rows
            </option>
          ))}
        </select>
      </div>

      {/* TABLE */}
      <div className="overflow-x-auto">
        <table className="table-auto w-full border-collapse border border-gray-300">
          <thead className="bg-blue-100">
            <tr>
              {Object.keys(data[0]).map((k) => (
                <th key={k} className="border px-4 py-2 text-sm font-semibold">
                  {k}
                </th>
              ))}
            </tr>
          </thead>

          <tbody>
            {paginated.map((row, i) => (
              <tr key={i} className="hover:bg-gray-50">
                {Object.values(row).map((val, j) => (
                  <td key={j} className="border px-4 py-2 text-sm">
                    {val}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* PAGINATION BUTTONS */}
      <div className="flex justify-between items-center mt-3">
        <button
          disabled={page === 1}
          onClick={() => setPage((p) => p - 1)}
          className="px-3 py-1 bg-gray-200 rounded disabled:opacity-50"
        >
          ⬅ Prev
        </button>

        <span className="text-sm font-semibold">
          Page {page} of {totalPages}
        </span>

        <button
          disabled={page === totalPages}
          onClick={() => setPage((p) => p + 1)}
          className="px-3 py-1 bg-gray-200 rounded disabled:opacity-50"
        >
          Next ➡
        </button>
      </div>
    </>
  );
}

export default function DashboardTimetable() {
  const [uploading, setUploading] = useState(false);
  const [loadingView, setLoadingView] = useState(false);
  const [records, setRecords] = useState([]);
  const [timetable, setTimetable] = useState([]);
  const [filteredTimetable, setFilteredTimetable] = useState([]);

  const [facultyList, setFacultyList] = useState([]);
  const [sectionList, setSectionList] = useState([]);
  const [semesterList, setSemesterList] = useState([]);

  const [selectedFaculty, setSelectedFaculty] = useState("");
  const [selectedSection, setSelectedSection] = useState("");
  const [selectedSemester, setSelectedSemester] = useState("");

  const [role, setRole] = useState("");
  const [user, setUser] = useState(null);

  const tableRef = useRef();
  const navigate = useNavigate();

  // ----------------------------------------------
  // AUTH CHECK
  // ----------------------------------------------
  useEffect(() => {
    const u = JSON.parse(localStorage.getItem("edu_user"));
    if (u?.role) {
      setRole(u.role.toUpperCase());
      setUser(u);
    } else navigate("/login");
  }, [navigate]);

  // ----------------------------------------------
  // LOGOUT
  // ----------------------------------------------
  const handleLogout = () => {
    localStorage.removeItem("edu_user");
    navigate("/login");
  };

  // ----------------------------------------------
  // UPLOAD FUNCTIONS
  // ----------------------------------------------
  const handleUpload = async (file, type) => {
    const formData = new FormData();
    formData.append("file", file);

    setUploading(true);
    try {
      const res = await API.post(`/upload/${type}`, formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      alert(res.data.message);
    } catch (err) {
      alert(err.response?.data?.detail || "Upload failed");
    } finally {
      setUploading(false);
    }
  };

  // ----------------------------------------------
  // VIEW UPLOADED DATA
  // ----------------------------------------------
  const handleView = async (type) => {
    setLoadingView(true);
    try {
      const res = await API.get(`/upload/${type}/view`);
      setRecords(res.data.data);
    } catch (err) {
      alert(err.response?.data?.detail || "No data found");
      setRecords([]);
    } finally {
      setLoadingView(false);
    }
  };

  // ----------------------------------------------
  // GENERATE TIMETABLE (BACKEND)
  // ----------------------------------------------
  const handleGenerate = async () => {
    try {
      const res = await API.post("/timetable/generate");
      alert(res.data.message || "Timetable generated successfully.");
    } catch (err) {
      alert(err.response?.data?.detail || "Generation failed");
    }
  };

  // ----------------------------------------------
  // VIEW TIMETABLE
  // ----------------------------------------------
  const handleViewTimetable = async () => {
    setLoadingView(true);

    try {
      const res = await API.get("/timetable/list");
      let data = res.data.timetable || [];

      // 🌟 FIXED — PROPER EXPANSION (ONLY 2 ENTRIES FOR T & P)
      let expanded = [];

      data.forEach((item) => {
        // Case 0: COE (Special exam block)
        if (item.Type === "COE") {

          expanded.push({
            faculty: item.Faculty || "Exam Department",
            subject: item.Subject || "COE Examination",
            section: item.Section,
            day: item.Day,
            time_slot: item.Slot,     // e.g., "09:00-11:00"
            slot2: item.Slot2 || null,
            room: item.Room || "Exam Hall",
            type: "COE",
            year: item.Semester,
            isGroupSplit: false,
          });

          return;  // VERY IMPORTANT → avoid processing under other rules
        }
                // Case 1: Grouped entries (T or P)

        if (item.Groups && Array.isArray(item.Groups)) {
          item.Groups.forEach((g) => {
            expanded.push({
              faculty: g.faculty?.trim() || "",
              subject: g.subject?.trim() || "",
              section: g.group?.trim() || "",   // A1 / A2
              day: item.Day?.trim() || "",
              time_slot: item.Slot?.trim() || "",
              slot2: item.Slot2?.trim() || null,   // ✅ REQUIRED FOR 2-HOUR MERGE
              room: g.room || "",
              type: item.Type || "",
              year: item.Semester,
              isGroupSplit: true,
            });
          });

          // ❌ REMOVED — no combined entry (this was causing 3 rows)
        }

        // Case 2: Normal entries (L / PDP / COE)
        else {
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

      data = expanded;

      // 🌟 Proper timeslot mapping
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

      data = data.map((i) => ({
        ...i,
        time_slot: mapSlot[i.time_slot] || i.time_slot,
        slot2: mapSlot[i.slot2] || i.slot2,
      }));

      setTimetable(data);
      setFilteredTimetable(data);

      // Dropdown lists
      setFacultyList([...new Set(data.map((i) => i.faculty).filter(Boolean))]);

      const mainSections = [...new Set(
        data
          .map((i) => i.section?.replace(/[0-9]/g, "").toUpperCase())
          .filter(Boolean)
      )];
      setSectionList(mainSections);

      setSemesterList([...new Set(data.map((i) => i.year))]);

      setSelectedFaculty("");
      setSelectedSection("");
      setSelectedSemester("");

    } catch (err) {
      alert(err.response?.data?.detail || "Timetable fetch failed");
    } finally {
      setLoadingView(false);
    }
  };


  // ----------------------------------------------
  // AUTO FILTER
  // ----------------------------------------------
  useEffect(() => {
    let filtered = timetable;

    if (selectedFaculty)
      filtered = filtered.filter(
        (t) => t.faculty.toLowerCase() === selectedFaculty.toLowerCase()
      );

    if (selectedSection)
      filtered = filtered.filter(
        (t) =>
          t.section?.replace(/[0-9]/g, "").toUpperCase() ===
          selectedSection.toUpperCase()
      );

    if (selectedSemester)
      filtered = filtered.filter((t) => Number(t.year) === Number(selectedSemester));

    setFilteredTimetable(filtered);
  }, [selectedFaculty, selectedSection, selectedSemester, timetable]);

  // ----------------------------------------------
  // PDF DOWNLOAD
  // ----------------------------------------------
const downloadPDF = async () => {
  const input = tableRef.current;
  if (!input) return alert("No timetable to export");

  // Clone for clean rendering
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
    [...el.children].forEach(sanitizeColors);
  };

  
  sanitizeColors(clone);

  // Apply PDF-friendly styling
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

    const reservedSpace = 40; // Header + signatures
    if (imgHeight > pageHeight - reservedSpace - 35) {
      imgHeight = pageHeight - reservedSpace - 35;
      imgWidth = imgHeight * aspectRatio;
    }

    const x = (pageWidth - imgWidth) / 2;
    const y = 40;

    // Top header
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

    pdf.setFontSize(11);
    pdf.text(
      `Generated by Admin | Academic Year: 2025–26`,
      pageWidth / 2,
      30,
      { align: "center" }
    );

    // Add table screenshot
    pdf.addImage(imgData, "PNG", x, y, imgWidth, imgHeight);

    // Footer + Signatures
    const date = new Date().toLocaleDateString("en-IN", {
      day: "2-digit",
      month: "short",
      year: "numeric",
    });

    const footerY = y + imgHeight + 18;

    // Divider line
    pdf.setDrawColor(180);
    pdf.setLineWidth(0.3);
    pdf.line(15, footerY - 10, pageWidth - 15, footerY - 10);

    // Signature lines
    const leftX = 35;
    const rightX = pageWidth - 105;
    const lineY = footerY - 4;

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

    // Footer stamp
    pdf.setFontSize(9);
    pdf.setTextColor(90);
    pdf.text(
      `Generated by EduChrono on ${date}`,
      pageWidth / 2,
      pageHeight - 8,
      { align: "center" }
    );

    pdf.save(`Admin_Timetable_${Date.now()}.pdf`);
  } catch (err) {
    console.error("PDF Error:", err);
    alert("Error generating PDF.");
  }
};

const downloadWord = async () => {
  try {
    const roleValue = user?.role?.toLowerCase() || "admin";
    const identifier = "all";

    const res = await fetch(
      `http://localhost:8000/timetable/download-word/${roleValue}/${identifier}`
    );

    if (!res.ok) {
      throw new Error("Failed to download Word file");
    }

    const blob = await res.blob();
    const url = window.URL.createObjectURL(blob);

    const a = document.createElement("a");
    a.href = url;
    a.download = "timetable.docx";
    document.body.appendChild(a);
    a.click();
    a.remove();

    window.URL.revokeObjectURL(url);

  } catch (err) {
    console.error("❌ Word Download Error:", err);
    alert("Word download failed ❌");
  }
};



  // ----------------------------------------------
  return (
    <div className="min-h-screen bg-gray-50 p-8">
      {/* HEADER */}
      <div className="flex justify-between items-center mb-8">
        <h2 className="text-3xl font-bold text-blue-700">
          📘 EduChrono | Timetable Dashboard ({role})
        </h2>
        <button
          onClick={handleLogout}
          className="bg-red-500 text-white px-4 py-2 rounded-md"
        >
          Logout
        </button>
      </div>

      {/* ADMIN CONTROLS */}
      {["ADMIN", "HOD"].includes(role) && (
        <>
          {/* UPLOAD PANEL */}
          <section className="bg-white p-6 rounded-xl shadow-md mb-10">
            <h3 className="text-xl font-semibold mb-4">⬆️ Upload Excel Data</h3>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* <FileUploader
                label="Upload Faculty Load"
                onUpload={(f) => handleUpload(f, "faculty-load")}
                onDownloadTemplate={() => window.open("http://localhost:8000/upload/template/faculty-load")}
              /> */}

              <FileUploader
                label="Upload Teaching Load"
                onUpload={(f) => handleUpload(f, "teaching-load")}
                onDownloadTemplate={() => window.open("http://localhost:8000/upload/template/teaching-load")}
              />

              <FileUploader
                label="Upload Room List"
                onUpload={(f) => handleUpload(f, "room-list")}
                onDownloadTemplate={() => window.open("http://localhost:8000/upload/template/room-list")}
              />

              {/* <FileUploader
                label="Upload Lab List"
                onUpload={(f) => handleUpload(f, "lab-list")}
                onDownloadTemplate={() => window.open("http://localhost:8000/upload/template/lab-list")}
              /> */}
            </div>
          </section>





{/* ========================== VIEW UPLOADED DATA ========================== */}
          <section className="bg-white p-6 rounded-xl shadow-md mb-10">
            <h3 className="text-xl font-semibold text-gray-700 mb-4">
              👁️ View Uploaded Data
            </h3>

            <div className="flex flex-wrap gap-4 mb-6">
              {/* <button
                onClick={() => handleView("faculty-load")}
                className="bg-blue-600 text-white px-4 py-2 rounded-md"
              >
                View Faculty Load
              </button> */}

              <button
                onClick={() => handleView("teaching-load")}
                className="bg-purple-600 text-white px-4 py-2 rounded-md"
              >
                View Teaching Load
              </button>

              <button
                onClick={() => handleView("room-list")}
                className="bg-green-600 text-white px-4 py-2 rounded-md"
              >
                View Room List
              </button>

              {/* <button
                onClick={() => handleView("lab-list")}
                className="bg-orange-600 text-white px-4 py-2 rounded-md"
              >
                View Lab List
              </button> */}
            </div>

            {!loadingView && records.length > 0 && (
              <SinglePaginationComponent data={records} />
            )}

          </section>

          {/* GENERATE + VIEW */}
          <section className="bg-white p-6 rounded-xl shadow-md">
            <h3 className="text-xl font-semibold mb-4">🧮 Generate & View Timetable</h3>

            <div className="flex flex-wrap gap-4 mb-6">
              {role === "ADMIN" && (
                <button
                  onClick={handleGenerate}
                  className="bg-green-600 text-white px-5 py-2 rounded-md"
                >
                  Generate Timetable
                </button>
              )}

              <button
                onClick={handleViewTimetable}
                className="bg-blue-700 text-white px-5 py-2 rounded-md"
              >
                View Generated Timetable
              </button>

              {timetable.length > 0 && (
                <>
                  <select
                    value={selectedFaculty}
                    onChange={(e) => setSelectedFaculty(e.target.value)}
                    className="border px-3 py-2 rounded-md"
                  >
                    <option value="">All Faculty</option>
                    {facultyList.map((f) => (
                      <option key={f}>{f}</option>
                    ))}
                  </select>

                  <select
                    value={selectedSection}
                    onChange={(e) => setSelectedSection(e.target.value)}
                    className="border px-3 py-2 rounded-md"
                  >
                    <option value="">All Sections</option>
                    {sectionList.map((s) => (
                      <option key={s}>{s}</option>
                    ))}
                  </select>

                  <select
                    value={selectedSemester}
                    onChange={(e) => setSelectedSemester(e.target.value)}
                    className="border px-3 py-2 rounded-md"
                  >
                    <option value="">All Semesters</option>
                    {semesterList.map((s) => (
                      <option key={s}>{s}</option>
                    ))}
                  </select>
                </>
              )}
            </div>

            {/* TABLE */}
            {!loadingView && filteredTimetable.length > 0 && (
              <div ref={tableRef} className="overflow-x-auto">
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
                    "4:00–5:00",
                  ]}
                />
              </div>
            )}

            {filteredTimetable.length > 0 && (
              <div className="text-right mt-4">
              <button
                onClick={downloadPDF}
                className="bg-blue-600 text-white px-4 py-2 rounded-md"
              >
                📄 Download PDF
              </button>
            
              <button
                onClick={downloadWord}
                className="bg-green-600 text-white px-4 py-2 rounded-md ml-2"
              >
                📝 Download Word
              </button>
            </div>
            )}
          </section>
        </>
      )}
    </div>
  );
}

