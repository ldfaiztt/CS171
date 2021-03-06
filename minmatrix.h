/*
 * Steven Mueller
 * diffusor@ugcs.caltech.edu
 * cs/cns 171  Spring 2004
 * this code is in the process of being released under the GNU GPLed
 */

/*
 * minmatrix.h -- minimal 2-D matrix library, implemented as templates of
 * multidimensional arrays.
 * 
 * A miniature matrix library for doing the things we need with transforms and
 * objects.
 */

#ifndef __MINMATRIX_H_GUARD__
#define __MINMATRIX_H_GUARD__

#include <iosfwd>
#include <cstdio>
#include <cassert>

/*
 * 2dim matrix class
 */
typedef unsigned long dimsize_t;

// Polymorphic exception tree
class MatrixException {
    public:
	virtual ~MatrixException() {};
};
class ZeroNormException : public MatrixException {};
class MatrixBoundsException : public MatrixException {};

/*
 * These matrices copy on assign and copy on copy-construct, allowing
 * reasonable temporaries, etc.  I've tried to make them generate as few such
 * copies as possible.  For instance, if compiled with -O2, a matrix * scalar
 * operation makes only one copy (on the stack frame of the caller).
 */
template<typename T, dimsize_t R, dimsize_t C>
class Matrix {
    public:
	// convenience typedefs
	typedef T data_t;
	// convenience dimensions
	static const dimsize_t nrows,ncols;

    private:
	data_t matrix[R*C];  // statically allocated matrix, accessed row-major

	// Debugging - -DWATCHMATRICES to view constructs/destructs/etc
#ifndef WATCHMATRICES
	void watch(const char *) const {} // should optimize away
#else
	void watch(const char *s) const { fprintf(stderr, "%s %p\n", s, this); }
#endif

    public:
	// accessors
	dimsize_t size() const { return nrows*ncols; }

	// Copy elements out of arr directly into the internal matrix
	void wipe_copy(const data_t *arr) {
	    for (dimsize_t i=0; i<size(); ++i) matrix[i]=arr[i]; }

	//---------------------------------------------------
	// Constructors and memory housekeeping
	//---------------------------------------------------

	// Constructor.  Initialize the m x n matrix,
	Matrix() { watch("Construct"); }

	// Destructor.
	virtual ~Matrix() { watch("Destruct"); }

	// Copy Constructor - deep copy of all data
	Matrix(const Matrix& m2) {
	    watch("copy");
	    m2.watch("from");
	    wipe_copy(m2.matrix); }

	// Assignment
	Matrix& operator= (const Matrix& m2) {
	    // DO NOT CHANGE THE ORDER OF THESE STATEMENTS!
	    // (This order properly handles self-assignment)
	    watch("assign");
	    m2.watch("from");
	    if (this!=&m2) {  // do nothing if it is the same object
		wipe_copy(m2.matrix);
	    }
	    return *this;
	}

	// Clear the matrix, setting each value as specified
	void clear(data_t val) { for (dimsize_t i=0; i<size(); i++) matrix[i]=val; }

	//---------------------------------------------------
	// element indexing -- row, col order
	//---------------------------------------------------

	// Return true if row,col is in bounds
	bool in_bounds(dimsize_t row, dimsize_t col) const {
	    return row>=0 && col>=0 && row<nrows && col<ncols;
	}
	// Return true if i is in bounds (accessing as a vector)
	bool in_bounds(dimsize_t i) const {
	    return i < size();
	}
	
	// Bounds-checking accessor
	const data_t &at(dimsize_t row, dimsize_t col) const {
	    if(in_bounds(row,col)) return ref(row,col);
	    else assert(in_bounds(row,col)); // XXX placeholder for exception throw
	}
	
	// Bounds-checking LValue setter
	data_t &at(dimsize_t row, dimsize_t col) {
	    if(in_bounds(row,col)) return ref(row,col);
	    else assert(in_bounds(row,col)); // XXX placeholder for exception throw
	}

	// non-checked accessor
	const data_t &ref(dimsize_t row, dimsize_t col) const { return matrix[col + row*ncols]; }

	// non-checked LValue setter
	data_t &ref(dimsize_t row, dimsize_t col) { return matrix[col + row*ncols]; }

	// nonchecked subscripting get/set
	const data_t &operator()(dimsize_t row, dimsize_t col) const { return ref(row,col); }
	data_t &operator()(dimsize_t row, dimsize_t col) { return ref(row,col); }

	// display the matrix prettilly.  TODO time?
	std::ostream &display(std::ostream &os) const;
	
	// Also do this flat addressability for faster blitting of matrix?
	const data_t &operator[](dimsize_t i) const { assert(in_bounds(i)); return matrix[i]; }
	data_t &operator[](dimsize_t i) { assert(in_bounds(i)); return matrix[i]; }
	const data_t &ref(dimsize_t i) const { return (*this)[i]; }
	data_t &ref(dimsize_t i) { return (*this)[i]; }
	    
    public:
	//ptr operator& () { ++count_; return ptr(this); }
	//---------------------------------------------------
	// fun operations
	//---------------------------------------------------

	// Return the magnitude (L2-norm) of the given vector
	T magnitude() const {
	    assert(R==1 || C==1);
	    T mag = 0;
	    // Accumulate the dot product
	    for (dimsize_t i=0; i<R*C; ++i)
		mag+=ref(i)*ref(i);
	    return sqrt(mag);
	}

	/* mutator:
	 * Normalize the given vector in place using the L2-norm:
	 * u=v/sqrt(sum(elements))
	 * (this handles 1.cols or rows.1 (row or column) vectors)
	 */
	void normalize() {
	    T mag=magnitude();
	    if (mag == 0) throw ZeroNormException();
	    *this /= mag;
	}

	// mutator:
	// copy the elements of m2 into this matrix at the given offset
	template<dimsize_t R2, dimsize_t C2>
	void inlay_from(const Matrix<T,R2,C2> &m2,
		dimsize_t rowOffset, dimsize_t colOffset) {
	    assert(m2.nrows + rowOffset <= nrows && m2.ncols+colOffset <= ncols);
	    // Address the row/col of the inlayed m2
	    for (dimsize_t row=0; row<m2.nrows; ++row)
		for (dimsize_t col=0; col<m2.ncols; ++col)
		    ref(row+rowOffset, col+colOffset)=m2(row,col);
	}

	// return true iff this has the same dimensions as m2
	//template<typename U, dimsize_t R_, dimsize_t C_>
	bool samedim(const Matrix &m2) const {
	    return nrows == m2.nrows && ncols == m2.ncols;
	}

};


template<typename T, dimsize_t R, dimsize_t C> const dimsize_t Matrix<T,R,C>::nrows = R;
template<typename T, dimsize_t R, dimsize_t C> const dimsize_t Matrix<T,R,C>::ncols = C;

// display the matrix in square bracket form: [[row1][row2]...[row n]].
template<typename T, dimsize_t R, dimsize_t C>
std::ostream &Matrix<T,R,C>::display(std::ostream &os) const {
    os << "[";
    for (dimsize_t j=0; j<nrows; ++j) {
	if(j > 0) os << " [";
	else os << "[";

	for (dimsize_t i=0; i<ncols; ++i)
	{
	    os.width(10);
	    os << ref(j,i) << " ";
	}
	os << "]";
	if(j < nrows - 1) os << std::endl;
    }
    os << "]" << std::endl;
    return os;
}


// read the matrix as a whitespace-delimited list of rows, each of which is
// a list of whitespace-separated matrix elements:
// e.g.: [[11 12 13] [21 22 23]]  << 11 12 13  21 22 23
// (no commas here!)
// TODO use sentry objects for atomicity
template<typename T, dimsize_t R, dimsize_t C>
std::istream &operator>>(std::istream &is, Matrix<T,R,C> &m) {
    for (dimsize_t j=0; j<m.nrows; ++j) {
	for (dimsize_t i=0; i<m.ncols; ++i) {
	    is >> m(j,i);
	}
    }
    return is;
}

// Dense matrix output
// output the matrix as a comma-delimited list of rows, each of which is
// a list of whitespace-separated matrix elements:
// e.g.: [[11 12 13] [21 22 23]]  >> 11 12 13, 21 22 23
template<typename T, dimsize_t R, dimsize_t C>
std::ostream &operator<<(std::ostream &os, const Matrix<T,R,C> &m) {
    for (dimsize_t row=0; row<m.nrows; ++row) {
	if (row > 0) os << ",";
	for (dimsize_t col=0; col<m.ncols; ++col) {
	    if (col > 0 || row > 0) os << " ";
	    os << m(row,col);
	}
    }
    return os;
}


//---------------------------------------------------------------------------
// Matrix Scalar Arithmetic
//---------------------------------------------------------------------------

// create operator+=(matrix, T), etc
#define MAKE_MATRIX_opeq_SCALAR(op, impop) \
template<typename T, dimsize_t R, dimsize_t C> \
Matrix<T,R,C> &op (Matrix<T,R,C> &m, T &scalar) { \
    for (dimsize_t i=0; i<m.size(); ++i) m.ref(i) impop scalar; \
    return m; \
}
MAKE_MATRIX_opeq_SCALAR(operator+=, +=)
MAKE_MATRIX_opeq_SCALAR(operator-=, -=)
MAKE_MATRIX_opeq_SCALAR(operator*=, *=)
MAKE_MATRIX_opeq_SCALAR(operator/=, /=)


// add matrices element by element
// Matrix types ensure that they will be of proper dimensionality
template<typename T, dimsize_t R, dimsize_t C>
Matrix<T,R,C> &operator+=(Matrix<T,R,C> &m1, const Matrix<T,R,C> &m2) {
    for (dimsize_t i=0; i<m1.size(); ++i) m1[i]+=m2[i];
    return m1;
}

template<typename T, dimsize_t R, dimsize_t C>
Matrix<T,R,C> &operator-=(Matrix<T,R,C> &m1, const Matrix<T,R,C> &m2) {
    assert(m1.samedim(m2));
    for (dimsize_t i=0; i<m1.size(); ++i) m1[i]-=m2[i];
    return m1;;
}


// create operator+(matrix, T), etc
#define MAKE_MATRIX_op_SCALAR(op, impop) \
template<typename T, dimsize_t R, dimsize_t C> \
Matrix<T,R,C> op (const Matrix<T,R,C> &m, T &scalar) { \
    Matrix<T,R,C> res(m); \
    res impop scalar; \
    return res; \
}
MAKE_MATRIX_op_SCALAR(operator+, +=)
MAKE_MATRIX_op_SCALAR(operator-, -=)
MAKE_MATRIX_op_SCALAR(operator*, *=)
MAKE_MATRIX_op_SCALAR(operator/, /=)

// element-wise addition/subtraction
template<typename T, dimsize_t R, dimsize_t C>
Matrix<T,R,C> operator+(const Matrix<T,R,C> &m1, const Matrix<T,R,C> &m2) {
    Matrix<T,R,C> res(m1);
    res+=m2;
    return res;
}
template<typename T, dimsize_t R, dimsize_t C>
Matrix<T,R,C> operator-(const Matrix<T,R,C> &m1, const Matrix<T,R,C> &m2) {
    Matrix<T,R,C> res(m1);
    res-=m2;
    return res;
}

// The other way
template<typename T, dimsize_t R, dimsize_t C>
Matrix<T,R,C> operator+(T scalar, const Matrix<T,R,C> &m) { return m + scalar; }
template<typename T, dimsize_t R, dimsize_t C>
Matrix<T,R,C> operator-(T scalar, const Matrix<T,R,C> &m) {
    Matrix<T,R,C> res(m);
    for (dimsize_t i=0; i<m.nrows*m.ncols; ++i) res[i]=scalar-res[i];
    return res;
}
template<typename T, dimsize_t R, dimsize_t C>
Matrix<T,R,C> operator*(T scalar, const Matrix<T,R,C> &m) { return m * scalar; }


// Return an n x n identity matrix.
template<typename T, dimsize_t N>
Matrix<T,N,N> identity() {
    Matrix<T,N,N> res;
    res.clear(0);
    for (dimsize_t i=0; i<N; ++i) res(i,i)=1;
    return res;
}

// Return an n x n matrix with the specified diagonal
template<typename T, dimsize_t R, dimsize_t C>
Matrix<T,N,N> diagonal(const Matrix<T,N,1> &m) {
    Matrix<T,N,N> res;
    res.clear(0);
    for (dimsize_t i=0; i<N; ++i) res(i,i)=m[i];
    return res;
}


//template<typename T, typename U> T implicit_cast(U u) { return u; }


//---------------------------------------------------------------------------
// Matrix operations
//---------------------------------------------------------------------------


// Calculate the dot product of the given row of m1 with the given column of
// m2.  Helper for matrix multiplication
template<typename T, dimsize_t CR, dimsize_t arbitraryR, dimsize_t arbitraryC>
T row_dot_col(const Matrix<T,arbitraryR,CR> &m1, dimsize_t row, const Matrix<T,CR,arbitraryC> &m2, dimsize_t col) {
    T sum=0;
    //std::cout << "Row " << row << " col " << col << " ";
    for (dimsize_t i=0; i<m1.ncols; ++i) {
	//std::cout << "+" << m1.ref(row,i) << "*" << m2.ref(i,col);
	sum+=m1.ref(row,i)*m2.ref(i,col);
    }
    //std::cout << std::endl;
    return sum;
}

// Matrix multiplication - Constructs a new data array for the result.
template<typename T, dimsize_t R, dimsize_t CR, dimsize_t C>
Matrix<T,R,C> operator*(const Matrix<T,R,CR> &m1, const Matrix<T,CR,C> &m2) {
    // Create a new matrix for the result
    Matrix<T,R,C> res;
    for(dimsize_t rrow=0; rrow<res.nrows; ++rrow)     // each row in result
	for(dimsize_t rcol=0; rcol<res.ncols; ++rcol) // each column in result
	    res.ref(rrow,rcol) = row_dot_col(m1, rrow, m2, rcol);
    return res;
}

// Return a new matrix that is the transpose of matrix m.
template<typename T, dimsize_t R, dimsize_t C>
Matrix<T,C,R> transpose(const Matrix<T,R,C> &m) {
    Matrix<T,C,R> res;
    // Address the row/col of the original m
    for (dimsize_t row=0; row<m.nrows; ++row)
	for (dimsize_t col=0; col<m.ncols; ++col)
	    res.ref(col,row)=m.ref(row,col);
    return res;
}


// Normalize the given vector in the standard way: u=v/sqrt(v.v)
// (this handles 1.n or m.1 type vectors)
template<typename T, dimsize_t R, dimsize_t C>
Matrix<T,R,C> normalize(const Matrix<T,R,C> &v) {
    Matrix<T,R,C> u(v);
    u.normalize(v);
    res /= mag;
    return res;
}

// Homogenize the given vector: divide the vector by the last component
// (this handles 1.n type vectors)
template<typename T, dimsize_t C>
Matrix<T,1,C> homogenize(const Matrix<T,1,C> &v) {
    Matrix<T,1,C> u(v);
    u.homogenize(v);
    res /= res.ref(1,col);
    return res;
}

// Homogenize the given vector: divide the vector by the last component
// (this handles m.1 type vectors)
template<typename T, dimsize_t R>
Matrix<T,R,1> homogenize(const Matrix<T,R,1> &v) {
    Matrix<T,R,1> u(v);
    u.homogenize(v);
    res /= res.ref(row,1)
    return res;
}

// Inverse of 4x4 matrix: returns the inverse
template<typename T, dimsize_t R, dimsize_t C>
Matrix<T,R,C> invert4(const Matrix<T,R,C>&A) {
  Matrix<T,R,C+1> wtemp;
  register float m1, m2, m3, s;
  // make r[0-3] hold pointers to the rows for row swaps
  Matrix<T,1,C+1> r0;
  Matrix<T,1,C+1> r1;
  Matrix<T,1,C+1> r2;
  Matrix<T,1,C+1> r3;

  for (dimsize_t i=0; i<m.ncols+1; ++i) {
    r0.ref(0,i) = wtemp.ref(0,i);
    r1.ref(0,i) = wtemp.ref(1,i);
    r2.ref(0,i) = wtemp.ref(2,i);
    r3.ref(0,i) = wtemp.ref(3,i);
  }

  register float *rtemp;
 
  // build the tmp matrix with the single rhs
  r0.ref(0,0) = A.ref(0,0); r0.ref(0,1) = A.ref(0,1); 
  r0.ref(0,2) = A.ref(0,2); r0.ref(0,3) = A.ref(0,3);
  r0[4] = b[0];
  r1[0] = A[1][0]; r1[1] = A[1][1]; r1[2] = A[1][2]; r1[3] = A[1][3];
  r1[4] = b[1];
  r2[0] = A[2][0]; r2[1] = A[2][1]; r2[2] = A[2][2]; r2[3] = A[2][3];
  r2[4] = b[2];
  r3[0] = A[3][0]; r3[1] = A[3][1]; r3[2] = A[3][2]; r3[3] = A[3][3];
  r3[4] = b[3];
}

// Return the magnitude of the given column vector
template<typename T, dimsize_t R>
T magnitude(const Matrix<T,R,1> &m) {
    return m.magnitude();
}

// Return the magnitude of the given row vector
template<typename T, dimsize_t C>
T magnitude(const Matrix<T,1,C> &m) {
    return m.magnitude();
}


/*
 *        Everything is parameterized over type T which could conceivably
 *        be anything like float (32 bit like OpenGL uses), double (64 bits)
 *        long double (80 bits) or even complex (possibly...)
 */
//typedef float coord_t;
typedef double coord_t;

typedef Matrix<coord_t,4,4> Hom4X4matrix;
typedef Matrix<coord_t,3,1> Vector3;
typedef Vector3 Point;

#endif // __MINMATRIX_H_GUARD__

