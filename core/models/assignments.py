import enum
from core import db
from core.apis.decorators import AuthPrincipal
from core.libs import helpers, assertions
from core.models.teachers import Teacher
from core.models.students import Student
from sqlalchemy.types import Enum as BaseEnum


class GradeEnum(str, enum.Enum):
    A = 'A'
    B = 'B'
    C = 'C'
    D = 'D'


class AssignmentStateEnum(str, enum.Enum):
    DRAFT = 'DRAFT'
    SUBMITTED = 'SUBMITTED'
    GRADED = 'GRADED'


class Assignment(db.Model):
    __tablename__ = 'assignments'
    id = db.Column(db.Integer, db.Sequence('assignments_id_seq'), primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey(Student.id), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey(Teacher.id), nullable=True)
    content = db.Column(db.Text)
    grade = db.Column(BaseEnum(GradeEnum))
    state = db.Column(BaseEnum(AssignmentStateEnum), default=AssignmentStateEnum.DRAFT, nullable=False)
    created_at = db.Column(db.TIMESTAMP(timezone=True), default=helpers.get_utc_now, nullable=False)
    updated_at = db.Column(db.TIMESTAMP(timezone=True), default=helpers.get_utc_now, nullable=False, onupdate=helpers.get_utc_now)

    def __repr__(self):
        return '<Assignment %r>' % self.id

    @classmethod
    def filter(cls, *criterion):
        db_query = db.session.query(cls)
        return db_query.filter(*criterion)

    @classmethod
    def get_by_id(cls, _id):
        return cls.filter(cls.id == _id).first()

    @classmethod
    def upsert(cls, assignment_new: 'Assignment'):
        # Ensuring content is not None or empty string with spaces
        assertions.assert_valid(
            assignment_new.content is not None and assignment_new.content.strip() != '',
            'Assignment content cannot be empty'
        )
    
        if assignment_new.id is not None:
            assignment = Assignment.get_by_id(assignment_new.id)
            assertions.assert_found(assignment, 'Assignment with the provided ID does not exist')
            assertions.assert_valid(
                assignment.state == AssignmentStateEnum.DRAFT,
                'Only assignments in the draft state can be edited'
            )

            assignment.content = assignment_new.content
        else:
            assignment = assignment_new
            db.session.add(assignment_new)

        db.session.flush()
        return assignment

    @classmethod
    def submit(cls, _id, teacher_id, auth_principal: AuthPrincipal):
        assignment = Assignment.get_by_id(_id)
        assertions.assert_found(assignment, 'Assignment with the provided ID does not exist')
        assertions.assert_valid(
            assignment.student_id == auth_principal.student_id,
            'Assignment belongs to another student'
        )
        assertions.assert_valid(
            assignment.content is not None,
            'Assignment content cannot be empty'
        )
        assertions.assert_valid(
            assignment.state == AssignmentStateEnum.DRAFT,
            'only a draft assignment can be submitted'
        )

        assignment.state = AssignmentStateEnum.SUBMITTED
        assignment.teacher_id = teacher_id
        db.session.flush()

        return assignment

    @classmethod
    def mark_grade(cls, _id, grade, auth_principal: AuthPrincipal):
        assignment = Assignment.get_by_id(_id)
        assertions.assert_found(assignment, 'Assignment with the provided ID does not exist')
        assertions.assert_valid(
            assignment.teacher_id == auth_principal.teacher_id,
            'Assignment belongs to another teacher'
        )
        assertions.assert_valid(
            grade is not None,
            'Grade cannot be empty'
        )
        assertions.assert_valid(
            assignment.state == AssignmentStateEnum.SUBMITTED,
            'Only submitted assignments can be graded'
        )

        assignment.grade = grade
        assignment.state = AssignmentStateEnum.GRADED
        db.session.flush()

        return assignment

    @classmethod
    def mark_grade_by_principal(cls, _id, grade):
        assignment = Assignment.get_by_id(_id)
        assertions.assert_found(assignment, 'Assignment with the provided ID does not exist')
        assertions.assert_valid(
            grade is not None,
            'Grade cannot be empty'
        )
        assertions.assert_valid(
            assignment.state in [AssignmentStateEnum.SUBMITTED, AssignmentStateEnum.GRADED],
            'Only submitted or graded assignments can be re-graded'
        )

        assignment.grade = grade
        assignment.state = AssignmentStateEnum.GRADED
        db.session.flush()

        return assignment

    @classmethod
    def get_assignments_by_student(cls, student_id):
        return cls.filter(cls.student_id == student_id).all()

    @classmethod
    def get_assignments_by_teacher(cls, teacher_id):
        return cls.filter(cls.teacher_id == teacher_id, cls.state != AssignmentStateEnum.DRAFT).all()
    
    @classmethod
    def get_assignments_by_principal(cls):
        return cls.filter(cls.state.in_([AssignmentStateEnum.SUBMITTED, AssignmentStateEnum.GRADED])).all()
