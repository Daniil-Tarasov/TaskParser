from sqlalchemy import Column, Integer, String, BigInteger, DateTime, ForeignKey, func, Index
from sqlalchemy.orm import declarative_base, relationship, Mapped
from typing import List

Base = declarative_base()


class Contest(Base):
    __tablename__ = "contests"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    codeforces_id: Mapped[int] = Column(Integer, unique=True, index=True)
    name: Mapped[str] = Column(String(255), nullable=False)
    type: Mapped[str] = Column(String(50))  # ICPC, Educational, etc.
    created_at: Mapped[DateTime] = Column(DateTime(timezone=True),
                                          server_default=func.now())

    problems: Mapped[List["Problem"]] = relationship("Problem",
                                                     back_populates="contest",
                                                     cascade="all, delete-orphan")


class Problem(Base):
    __tablename__ = "problems"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    codeforces_id: Mapped[str] = Column(String(20), unique=True, index=True)  # "1234A"
    contest_id: Mapped[int] = Column(Integer, ForeignKey("contests.id"), index=True)
    name: Mapped[str] = Column(String(255), nullable=False)
    rating: Mapped[int] = Column(Integer)  # Сложность 800, 1200, etc.
    solved_count: Mapped[BigInteger] = Column(BigInteger, default=0)
    index: Mapped[str] = Column(String(10))  # "A", "B", "C"

    contest: Mapped["Contest"] = relationship("Contest", back_populates="problems")
    tags: Mapped[List["ProblemTag"]] = relationship("ProblemTag",
                                                    back_populates="problem")
    def __repr__(self) -> str:
        return f"Problem(id={self.id}, name='{self.name}', rating={self.rating})"


class ProblemTag(Base):
    __tablename__ = "problem_tags"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    problem_id: Mapped[int] = Column(Integer, ForeignKey("problems.id"), index=True)
    tag: Mapped[str] = Column(String(100), index=True)  # "math", "graphs", "dp"

    problem: Mapped["Problem"] = relationship("Problem", back_populates="tags")

    def __repr__(self) -> str:
        return f"ProblemTag(problem_id={self.problem_id}, tag='{self.tag}')"


Index('ix_problems_rating_nonnull', Problem.rating, postgresql_where=Problem.rating.isnot(None))
