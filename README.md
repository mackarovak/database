Задача-3: 

Выражение РА и запрос на языке РИК, решающие задачу:
    
Все профессии, такие что:
Имеется участок в цехе 7
все рабочие этой профессии на этом участке имеют разряд > 4.

РИК:
    
    НАЙТИ { p.name_prof | p ∈ professions ∧ (∃ l ∈ lichsostav : (l.number_cex = 7 ∧ l.code = p.code_id ∧ l.razryad > 4)) ∧ (∀ l ∈ lichsostav : (l.number_cex = 7 ∧ l.code = p.code_id) → l.razryad > 4) }