
export default function Pagination({ itemsPerPage, totalItems, paginate }) {
    const pageNumbers = [];
  
    // for loop to calculate number of total pages. Then pushes (appends) to the pageNumbers array 
    for (let i = 1; i <= Math.ceil(totalItems / itemsPerPage); i++) {
      pageNumbers.push(i);
    }
  
    
    // JSX content. Lists all the pages that are within this data set
    return (
      <nav>
        <ul className="pagination">
          {pageNumbers.map(number => (
            <li key={number} className="page-item">
              <a onClick={() => paginate(number)} href="#" className="page-link">
                {number}
              </a>
            </li>
          ))}
        </ul>
      </nav>
    );
  };
  