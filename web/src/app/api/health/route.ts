import { NextResponse } from "next/server";

const API_URL =
  process.env.KUNORA_API_URL ?? "http://127.0.0.1:8000";

export async function GET() {
  try {
    const response = await fetch(`${API_URL}/health`, {
      cache: "no-store",
    });

    if (!response.ok) {
      return NextResponse.json(
        { status: "unavailable" },
        { status: 503 },
      );
    }

    return NextResponse.json({
      status: "healthy",
    });
  } catch {
    return NextResponse.json(
      { status: "unavailable" },
      { status: 503 },
    );
  }
}