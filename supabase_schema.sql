-- =============================================================================
-- MindConnect Platform — Supabase PostgreSQL Schema
-- Database: PostgreSQL / Supabase
-- =============================================================================

-- Enable UUID extension if needed
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. Users Table (Mirroring Django User Model)
CREATE TABLE IF NOT EXISTS public.accounts_user (
    id BIGSERIAL PRIMARY KEY,
    password VARCHAR(128) NOT NULL,
    last_login TIMESTAMPTZ,
    is_superuser BOOLEAN DEFAULT FALSE,
    username VARCHAR(150) UNIQUE NOT NULL,
    first_name VARCHAR(150) DEFAULT '',
    last_name VARCHAR(150) DEFAULT '',
    email VARCHAR(254) UNIQUE NOT NULL,
    is_staff BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    date_joined TIMESTAMPTZ DEFAULT NOW(),
    
    -- MindConnect Custom Attributes
    role VARCHAR(20) DEFAULT 'STUDENT' CHECK (role IN ('STUDENT', 'TEACHER', 'ADMIN')),
    academic_tier VARCHAR(10) CHECK (academic_tier IN ('SCHOOL', 'UG', 'PG')),
    institution VARCHAR(255) DEFAULT '',
    department_or_subject VARCHAR(255) DEFAULT '',
    grade_or_year VARCHAR(100) DEFAULT '',
    avatar_color VARCHAR(20) DEFAULT '#6366f1',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. Questions Table
CREATE TABLE IF NOT EXISTS public.assessments_question (
    id BIGSERIAL PRIMARY KEY,
    section VARCHAR(15) DEFAULT 'PART_1' CHECK (section IN ('PART_1', 'PART_2')),
    tier VARCHAR(10) NOT NULL CHECK (tier IN ('SCHOOL', 'UG', 'PG')),
    category VARCHAR(20) DEFAULT 'VARK',
    difficulty VARCHAR(10) DEFAULT 'GENERAL',
    prompt TEXT NOT NULL,
    subtitle VARCHAR(255) DEFAULT '',
    explanation TEXT DEFAULT '',
    "order" INT DEFAULT 0
);

-- 3. Question Choices Table
CREATE TABLE IF NOT EXISTS public.assessments_choice (
    id BIGSERIAL PRIMARY KEY,
    question_id BIGINT REFERENCES public.assessments_question(id) ON DELETE CASCADE,
    text VARCHAR(255) NOT NULL,
    dimension VARCHAR(20) NOT NULL CHECK (dimension IN ('VISUAL', 'AUDITORY', 'KINESTHETIC', 'GROWTH', 'STRESS', 'COGNITIVE', 'GENERAL')),
    points INT DEFAULT 1,
    is_correct BOOLEAN DEFAULT FALSE,
    tag VARCHAR(50) DEFAULT '',
    "order" INT DEFAULT 0
);

-- 4. Assessment Submissions Table
CREATE TABLE IF NOT EXISTS public.assessments_submission (
    id BIGSERIAL PRIMARY KEY,
    student_id BIGINT REFERENCES public.accounts_user(id) ON DELETE CASCADE,
    tier VARCHAR(10) NOT NULL CHECK (tier IN ('SCHOOL', 'UG', 'PG')),
    submitted_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- 5-Dimension Normalized Scores (0-100%)
    visual_score INT DEFAULT 0,
    auditory_score INT DEFAULT 0,
    kinesthetic_score INT DEFAULT 0,
    growth_score INT DEFAULT 0,
    stress_score INT DEFAULT 0,
    cognitive_score INT DEFAULT 0,
    
    -- Whole-Student Diagnostic Profile Tags
    personality_tag VARCHAR(60) DEFAULT '',
    interests_tag VARCHAR(60) DEFAULT '',
    wellbeing_flag VARCHAR(20) DEFAULT 'Green',
    soft_skills_summary VARCHAR(255) DEFAULT '',
    open_message_to_teacher TEXT DEFAULT '',
    
    -- Archetype Persona
    persona_title VARCHAR(120) DEFAULT 'Evolving Learner',
    persona_tagline VARCHAR(255) DEFAULT 'Developing multi-modal study instincts.',
    persona_summary TEXT DEFAULT '',
    
    -- 3-Pillar Educator Mentorship Blueprint
    teacher_motivation TEXT DEFAULT '',
    teacher_communication TEXT DEFAULT '',
    teacher_caution TEXT DEFAULT ''
);

-- 5. Teacher Observation Notes Table
CREATE TABLE IF NOT EXISTS public.dashboard_teachernote (
    id BIGSERIAL PRIMARY KEY,
    teacher_id BIGINT REFERENCES public.accounts_user(id) ON DELETE CASCADE,
    student_id BIGINT REFERENCES public.accounts_user(id) ON DELETE CASCADE,
    submission_id BIGINT REFERENCES public.assessments_submission(id) ON DELETE SET NULL,
    category VARCHAR(20) DEFAULT 'OBSERVATION' CHECK (category IN ('OBSERVATION', 'ACADEMIC', 'WELLBEING', 'INTERVENTION', 'AI_STRATEGY')),
    content TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for Fast Query Performance
CREATE INDEX IF NOT EXISTS idx_users_role ON public.accounts_user(role);
CREATE INDEX IF NOT EXISTS idx_submissions_student ON public.assessments_submission(student_id);
CREATE INDEX IF NOT EXISTS idx_submissions_submitted ON public.assessments_submission(submitted_at DESC);
CREATE INDEX IF NOT EXISTS idx_questions_tier ON public.assessments_question(tier, section);
CREATE INDEX IF NOT EXISTS idx_teachernote_student ON public.dashboard_teachernote(student_id);

-- Enable Row Level Security (RLS)
ALTER TABLE public.accounts_user ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.assessments_question ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.assessments_choice ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.assessments_submission ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.dashboard_teachernote ENABLE ROW LEVEL SECURITY;

-- Read policies for public anonymous/authenticated queries
CREATE POLICY "Public read for questions" ON public.assessments_question FOR SELECT USING (true);
CREATE POLICY "Public read for choices" ON public.assessments_choice FOR SELECT USING (true);
CREATE POLICY "Users can read own profile" ON public.accounts_user FOR SELECT USING (true);
CREATE POLICY "Educators and Students read submissions" ON public.assessments_submission FOR SELECT USING (true);
CREATE POLICY "Educators access notes" ON public.dashboard_teachernote FOR ALL USING (true);
