import { useState, useEffect } from "react";
import { X } from "lucide-react";

interface CoordinatePickerProps {
  isOpen: boolean;
  onClose: () => void;
  onPick: (x: number, y: number) => void;
}

export default function CoordinatePicker({ isOpen, onClose, onPick }: CoordinatePickerProps) {
  const [position, setPosition] = useState({ x: 0, y: 0 });
  const [isPicking, setIsPicking] = useState(false);

  useEffect(() => {
    if (!isOpen) {
      setIsPicking(false);
      return;
    }

    // Show instructions to user
    const confirmStart = window.confirm(
      "Click OK to start picking coordinates.\n\n" +
      "After clicking OK:\n" +
      "1. Move your mouse to see current position\n" +
      "2. Click anywhere to capture coordinates\n" +
      "3. Click Cancel to stop"
    );

    if (confirmStart) {
      setIsPicking(true);
      
      // Track mouse position
      const handleMouseMove = (e: MouseEvent) => {
        if (isPicking) {
          setPosition({ x: e.clientX, y: e.clientY });
        }
      };

      // Capture click
      const handleClick = (e: MouseEvent) => {
        if (isPicking) {
          e.preventDefault();
          e.stopPropagation();
          setIsPicking(false);
          onPick(e.clientX, e.clientY);
          onClose();
          
          // Remove listeners
          document.removeEventListener("mousemove", handleMouseMove);
          document.removeEventListener("click", handleClick, true);
        }
      };

      // Add listeners
      document.addEventListener("mousemove", handleMouseMove);
      document.addEventListener("click", handleClick, true);

      return () => {
        document.removeEventListener("mousemove", handleMouseMove);
        document.removeEventListener("click", handleClick, true);
      };
    }
  }, [isOpen, isPicking, onPick, onClose]);

  if (!isOpen) return null;

  return (
    <div className="fixed top-4 right-4 z-50 bg-white rounded-lg shadow-xl border border-slate-200 p-4 w-64">
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-semibold text-slate-900">Pick Coordinates</h3>
        <button
          onClick={onClose}
          className="text-slate-400 hover:text-slate-600"
        >
          <X size={16} />
        </button>
      </div>
      
      {isPicking ? (
        <div className="space-y-3">
          <div className="bg-blue-50 border border-blue-200 rounded p-2 text-sm">
            <p className="text-blue-800 font-medium mb-1">Move your cursor...</p>
            <p className="text-blue-600 text-xs">Click anywhere to capture</p>
          </div>
          
          <div className="grid grid-cols-2 gap-2 text-sm">
            <div className="bg-slate-100 rounded px-3 py-2">
              <span className="text-slate-500 text-xs block">X</span>
              <span className="font-mono font-semibold">{position.x}</span>
            </div>
            <div className="bg-slate-100 rounded px-3 py-2">
              <span className="text-slate-500 text-xs block">Y</span>
              <span className="font-mono font-semibold">{position.y}</span>
            </div>
          </div>
          
          <button
            onClick={() => {
              setIsPicking(false);
              onClose();
            }}
            className="w-full py-2 px-3 rounded bg-slate-200 hover:bg-slate-300 text-slate-700 font-medium text-sm transition-colors"
          >
            Cancel
          </button>
        </div>
      ) : (
        <div className="text-center py-4">
          <p className="text-slate-500 text-sm">Starting picker...</p>
        </div>
      )}
    </div>
  );
}
