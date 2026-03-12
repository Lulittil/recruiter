-- Fix vacancies sequence to be in sync with existing data
SELECT setval('vacancies_vacancy_id_seq', COALESCE((SELECT MAX(vacancy_id) FROM vacancies), 1), true);

