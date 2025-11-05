"use client";

import { useState, useEffect } from 'react';
import Link from "next/link";
import Image from "next/image";

export default function HomePage() {
  const [isLoaded, setIsLoaded] = useState(false);

  useEffect(() => {
    setIsLoaded(true);
  }, []);

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100 relative overflow-hidden">
      {/* Subtle Background Pattern */}
      <div className="absolute inset-0 opacity-30">
        <div className="absolute top-20 left-20 w-64 h-64 bg-blue-200 rounded-full mix-blend-multiply filter blur-xl animate-pulse"></div>
        <div className="absolute bottom-32 right-32 w-72 h-72 bg-purple-200 rounded-full mix-blend-multiply filter blur-xl animate-pulse" style={{ animationDelay: "2s" }}></div>
        <div className="absolute top-1/2 left-1/3 w-56 h-56 bg-indigo-200 rounded-full mix-blend-multiply filter blur-xl animate-pulse" style={{ animationDelay: "4s" }}></div>
      </div>

      {/* Main Content Container */}
      <div className="relative z-10 min-h-screen flex items-center justify-center px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto w-full">
          <div className="grid lg:grid-cols-2 gap-16 items-center">
            
            {/* Left Side - Text Content */}
            <div className={`text-center lg:text-left space-y-10 transition-all duration-1000 ${isLoaded ? 'opacity-100 translate-x-0' : 'opacity-0 -translate-x-10'}`}>
              
              {/* Main Title */}
              <div className="space-y-6">
                <h1 className="text-5xl sm:text-6xl lg:text-7xl font-bold bg-gradient-to-r from-blue-600 via-purple-600 to-indigo-600 bg-clip-text text-transparent leading-tight">
                  Attendance Management System
                </h1>
              </div>

              {/* Action Buttons */}
              <div className="flex flex-col sm:flex-row gap-6 justify-center lg:justify-start">
                <Link
                  href="/signin"
                  className="group relative px-10 py-5 bg-white text-blue-600 font-bold text-lg rounded-2xl border-3 border-blue-300 hover:border-blue-400 transition-all duration-300 hover:scale-105 hover:shadow-2xl hover:-translate-y-2 shadow-lg"
                >
                  <span className="relative z-10">Sign In</span>
                  <div className="absolute inset-0 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                </Link>
                
                <Link
                  href="/signup"
                  className="group relative px-10 py-5 bg-gradient-to-r from-blue-600 to-indigo-600 text-white font-bold text-lg rounded-2xl transition-all duration-300 hover:scale-105 hover:shadow-2xl hover:-translate-y-2 shadow-lg overflow-hidden"
                >
                  <span className="relative z-10">Get Started</span>
                  <div className="absolute inset-0 bg-gradient-to-r from-blue-700 to-indigo-700 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                  <div className="absolute inset-0 bg-gradient-to-r from-white/10 to-white/10 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                </Link>
              </div>
            </div>

            {/* Right Side - Logo */}
            <div className={`flex justify-center lg:justify-end transition-all duration-1000 delay-300 ${isLoaded ? 'opacity-100 translate-x-0' : 'opacity-0 translate-x-10'}`}>
              <div className="relative">
                {/* Logo Container with Enhanced Styling */}
                <div className="relative w-96 h-96 sm:w-[450px] sm:h-[450px] lg:w-[500px] lg:h-[500px]">
                  {/* Glowing Background Effect */}
                  <div className="absolute inset-0 bg-gradient-to-br from-blue-400/30 via-purple-400/20 to-indigo-500/30 rounded-full blur-3xl animate-pulse"></div>
                  
                  {/* Main Logo Container */}
                  <div className="relative w-full h-full bg-white/90 backdrop-blur-lg rounded-3xl p-12 shadow-2xl border border-white/30 hover:shadow-3xl transition-all duration-500 hover:scale-105">
                    <div className="w-full h-full relative">
                      <Image
                        src="/logo/download.png"
                        alt="Attendance Management System Logo"
                        fill
                        className="object-contain drop-shadow-2xl"
                        priority
                      />
                    </div>
                  </div>

                  {/* Decorative Floating Elements */}
                  <div className="absolute -top-6 -right-6 w-12 h-12 bg-blue-500 rounded-full animate-bounce shadow-lg"></div>
                  <div className="absolute -bottom-6 -left-6 w-8 h-8 bg-purple-500 rounded-full animate-bounce shadow-lg" style={{ animationDelay: "1s" }}></div>
                  <div className="absolute top-1/3 -left-10 w-6 h-6 bg-indigo-500 rounded-full animate-bounce shadow-lg" style={{ animationDelay: "2s" }}></div>
                  <div className="absolute bottom-1/3 -right-8 w-10 h-10 bg-pink-500 rounded-full animate-bounce shadow-lg" style={{ animationDelay: "0.5s" }}></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Enhanced Custom CSS for animations and effects */}
      <style jsx global>{`
        @keyframes float {
          0%, 100% {
            transform: translateY(0px) rotate(0deg);
          }
          50% {
            transform: translateY(-25px) rotate(5deg);
          }
        }
        
        @keyframes bounce {
          0%, 100% {
            transform: translateY(0);
          }
          50% {
            transform: translateY(-10px);
          }
        }
        
        .animate-bounce {
          animation: bounce 2s infinite;
        }
        
        /* Enhanced button hover effects */
        .group:hover .absolute {
          transform: scale(1.02);
        }
        
        /* Mobile responsive adjustments */
        @media (max-width: 1024px) {
          .text-7xl {
            font-size: 3.5rem;
          }
        }
        
        @media (max-width: 768px) {
          .text-7xl {
            font-size: 2.5rem;
          }
          .text-6xl {
            font-size: 2rem;
          }
          .text-5xl {
            font-size: 1.75rem;
          }
        }
        
        @media (max-width: 640px) {
          .text-7xl {
            font-size: 2rem;
          }
          .text-6xl {
            font-size: 1.75rem;
          }
          .text-5xl {
            font-size: 1.5rem;
          }
        }
        
        /* Smooth scroll behavior */
        html {
          scroll-behavior: smooth;
        }
        
        /* Enhanced shadow effects */
        .shadow-3xl {
          box-shadow: 0 35px 60px -12px rgba(0, 0, 0, 0.25);
        }
        
        /* Custom gradient border */
        .border-3 {
          border-width: 3px;
        }
      `}</style>
    </main>
  );
}
