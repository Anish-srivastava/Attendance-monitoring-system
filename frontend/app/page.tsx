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
    <main className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50 relative overflow-hidden">
      {/* Animated Background Elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-4 -right-4 w-72 h-72 bg-blue-100 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-float"></div>
        <div className="absolute -bottom-8 -left-4 w-72 h-72 bg-purple-100 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-float" style={{ animationDelay: "2s" }}></div>
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-72 h-72 bg-pink-100 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-float" style={{ animationDelay: "4s" }}></div>
      </div>

      {/* Main Content Container */}
      <div className="relative z-10 min-h-screen flex items-center justify-center px-4 sm:px-6 lg:px-8">
        <div className="max-w-6xl mx-auto w-full">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            
            {/* Left Side - Content */}
            <div className={`text-center lg:text-left space-y-8 transition-all duration-1000 ${isLoaded ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'}`}>
              
              {/* Main Title */}
              <div className="space-y-4">
                <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold bg-gradient-to-r from-blue-600 via-purple-600 to-indigo-600 bg-clip-text text-transparent leading-tight">
                  Attendance Management System
                </h1>
                <p className="text-lg sm:text-xl text-gray-600 max-w-lg mx-auto lg:mx-0">
                  Revolutionary face recognition technology for seamless attendance tracking
                </p>
              </div>

              {/* Action Buttons */}
              <div className="flex flex-col sm:flex-row gap-4 justify-center lg:justify-start">
                <Link
                  href="/signin"
                  className="group relative px-8 py-4 bg-white text-blue-600 font-semibold rounded-2xl border-2 border-blue-200 hover:border-blue-300 transition-all duration-300 hover:scale-105 hover:shadow-xl hover:-translate-y-1"
                >
                  <span className="relative z-10">Sign In</span>
                  <div className="absolute inset-0 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                </Link>
                
                <Link
                  href="/signup"
                  className="group relative px-8 py-4 bg-gradient-to-r from-blue-600 to-indigo-600 text-white font-semibold rounded-2xl transition-all duration-300 hover:scale-105 hover:shadow-xl hover:-translate-y-1 overflow-hidden"
                >
                  <span className="relative z-10">Get Started</span>
                  <div className="absolute inset-0 bg-gradient-to-r from-blue-700 to-indigo-700 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                </Link>
              </div>

              {/* Feature Pills */}
              <div className="flex flex-wrap gap-3 justify-center lg:justify-start">
                <span className="px-4 py-2 bg-white/70 backdrop-blur-lg rounded-full text-sm font-medium text-gray-700 border border-gray-200">
                  🚀 Fast & Accurate
                </span>
                <span className="px-4 py-2 bg-white/70 backdrop-blur-lg rounded-full text-sm font-medium text-gray-700 border border-gray-200">
                  🔒 Secure
                </span>
                <span className="px-4 py-2 bg-white/70 backdrop-blur-lg rounded-full text-sm font-medium text-gray-700 border border-gray-200">
                  📱 Mobile Friendly
                </span>
              </div>
            </div>

            {/* Right Side - Logo */}
            <div className={`flex justify-center lg:justify-end transition-all duration-1000 delay-300 ${isLoaded ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'}`}>
              <div className="relative">
                {/* Logo Container with Floating Animation */}
                <div className="relative w-80 h-80 sm:w-96 sm:h-96 lg:w-[400px] lg:h-[400px] animate-float">
                  <div className="absolute inset-0 bg-gradient-to-br from-blue-400/20 to-indigo-500/20 rounded-full blur-3xl"></div>
                  <div className="relative w-full h-full bg-white/80 backdrop-blur-lg rounded-3xl p-8 shadow-2xl border border-white/20">
                    <div className="w-full h-full relative">
                      <Image
                        src="/logo/download.png"
                        alt="Attendance Management System Logo"
                        fill
                        className="object-contain drop-shadow-lg"
                        priority
                      />
                    </div>
                  </div>
                </div>

                {/* Decorative Elements */}
                <div className="absolute -top-4 -right-4 w-8 h-8 bg-blue-500 rounded-full animate-pulse"></div>
                <div className="absolute -bottom-4 -left-4 w-6 h-6 bg-purple-500 rounded-full animate-pulse" style={{ animationDelay: "1s" }}></div>
                <div className="absolute top-1/2 -left-8 w-4 h-4 bg-indigo-500 rounded-full animate-pulse" style={{ animationDelay: "2s" }}></div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Custom CSS for animations */}
      <style jsx global>{`
        @keyframes float {
          0%, 100% {
            transform: translateY(0px);
          }
          50% {
            transform: translateY(-20px);
          }
        }
        
        .animate-float {
          animation: float 6s ease-in-out infinite;
        }
        
        /* Mobile responsive adjustments */
        @media (max-width: 768px) {
          .animate-float {
            animation: float 4s ease-in-out infinite;
          }
        }
        
        /* Smooth scroll behavior */
        html {
          scroll-behavior: smooth;
        }
        
        /* Custom hover effects */
        .group:hover .absolute {
          transform: scale(1.05);
        }
      `}</style>
    </main>
  );
}
