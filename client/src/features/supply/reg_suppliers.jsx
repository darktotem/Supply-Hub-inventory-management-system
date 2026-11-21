import { useState, useEffect} from 'react'
import { getSuppliers, registerSupplier, deleteSupplier } from '../../api/supply'
import './supply.css'

function RegSuppliers() {
    const [suppliers, setSuppliers] = useState([])
    const [message, setMessage] = useState('')
    const [formData, setFormData] = useState({
        name: '',
        contact_person: '',
        email: '',
        phone: '',
        address: ''
    })
    const [searchTerm, setSearchTerm] = useState('')
    const [page, setPage] = useState(1)
    const PAGE_SIZE = 8

    //Fetch all registered suppliers
    const fetchSuppliers = async () => {
        try {
            const data = await getSuppliers()
            setSuppliers(data)
        } catch (error) {
            console.error('Error fetching suppliers:', error)
            setMessage(error.message)
        }
    }
    
    //Fetch suppliers on component mount
    useEffect(() => {
        fetchSuppliers()
    }, [])
    
    //Handle form input changes
    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value
        })
    }
    
    //Register a new supplier
    const handleSubmit = async (e) => {
        e.preventDefault()
        setMessage('')

        try {
            const data = await registerSupplier(formData)
                 
            setSuppliers(prevSuppliers => [...prevSuppliers, data])
            setMessage('Supplier registered successfully.')

            setFormData({
                name: '',
                contact_person: '',
                email: '',
                phone: '',
                address: ''
            })
        } catch (error) {
            setMessage(error.message)
        }
    }
    
    //Delete a supplier
    const handleDelete = async (id) => {
        setMessage('')

        try {
            await deleteSupplier(id)
           
            setSuppliers(prevSuppliers => prevSuppliers.filter(supplier => supplier.id !== id))
            setMessage('Supplier deleted successfully.')
        } catch (error) {
            setMessage(error.message)
        }
    }

    
    const filteredSuppliers = suppliers.filter((supplier) => {
        const search = searchTerm.toLowerCase()
        return (
            (supplier.name || '').toLowerCase().includes(search) ||
            (supplier.contact_person || '').toLowerCase().includes(search) ||
            (supplier.email || '').toLowerCase().includes(search)
        )
    })

    const totalPages = Math.max(1, Math.ceil(filteredSuppliers.length / PAGE_SIZE))
    const currentPage = Math.min(page, totalPages)
    const pagedSuppliers = filteredSuppliers.slice(
        (currentPage - 1) * PAGE_SIZE,
        currentPage * PAGE_SIZE
    )

    return (
        <div className="suppliers-page">
            <h2>Register Suppliers</h2>
            <p>Manage your registered suppliers.</p>

            {message && <p className="message">{message}</p>}

            <div className="stat-cards">
                <div className="stat-card">
                    <div className="stat-header">
                        <span className="stat-icon stat-icon-total">🏢</span>
                        <span className="stat-label">Total Suppliers</span>
                    </div>
                    <span className="stat-value">{suppliers.length}</span>
                    <span className="stat-badge stat-badge-total">Registered</span>
                </div>
            </div>

            <form onSubmit={handleSubmit} className="supplier-form">
                <h3>Register New Supplier</h3>

                <input
                    type="text"
                    name="name"
                    placeholder="Supplier Name"
                    value={formData.name}
                    onChange={handleChange}
                    required
                />

                <input
                    type="text"
                    name="contact_person"
                    placeholder="Contact Person"
                    value={formData.contact_person}
                    onChange={handleChange}
                    required
                />

                <input
                    type="email"
                    name="email"
                    placeholder="Email Address"
                    value={formData.email}
                    onChange={handleChange}
                    required
                />
                <input
                    type="tel"
                    name="phone"
                    placeholder="Phone Number"
                    value={formData.phone}
                    onChange={handleChange}
                    required
                />
                <input
                    type="text"
                    name="address"
                    placeholder="Supplier Address"
                    value={formData.address}
                    onChange={handleChange}
                    required
                />
                <button type="submit">Register Supplier</button>
            </form>

            <div className="supplier-list">
                <h3>Supplier List</h3>

                <div className="filters">
                    <input
                        type="text"
                        placeholder="Search by name, contact person or email..."
                        value={searchTerm}
                        onChange={(e) => {
                            setSearchTerm(e.target.value)
                            setPage(1)
                        }}
                    />
                </div>

                {suppliers.length === 0 ? (
                    <p>No suppliers registered yet.</p>
                ) : filteredSuppliers.length === 0 ? (
                    <p>No suppliers match your search.</p>
                ) : (
                    <>
                        <table>
                            <thead>
                                <tr>
                                    <th>Name</th>
                                    <th>Contact Person</th>
                                    <th>Email</th>
                                    <th>Phone</th>
                                    <th>Address</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                
                                {pagedSuppliers.map((supplier) => (
                                    <tr key={supplier.id}>
                                        <td>{supplier.name}</td>
                                        <td>{supplier.contact_person}</td>
                                        <td>{supplier.email}</td>
                                        <td>{supplier.phone}</td>
                                        <td>{supplier.address}</td>
                                        <td>
                                            <button
                                                type="button"
                                                className="delete-btn"
                                                onClick={() => handleDelete(supplier.id)}
                                            >
                                                Delete
                                            </button>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>

                        <div className="pagination">
                            <span className="pagination-info">
                                Showing {(currentPage - 1) * PAGE_SIZE + 1}-
                                {Math.min(currentPage * PAGE_SIZE, filteredSuppliers.length)} of {filteredSuppliers.length} suppliers
                            </span>

                            <div className="pagination-buttons">
                                <button
                                    type="button"
                                    onClick={() => setPage(currentPage - 1)}
                                    disabled={currentPage === 1}
                                >
                                    &lt;
                                </button>

                                {Array.from({ length: totalPages }, (_, index) => index + 1).map((number) => (
                                    <button
                                        type="button"
                                        key={number}
                                        className={number === currentPage ? 'active' : ''}
                                        onClick={() => setPage(number)}
                                    >
                                        {number}
                                    </button>
                                ))}

                                <button
                                    type="button"
                                    onClick={() => setPage(currentPage + 1)}
                                    disabled={currentPage === totalPages}
                                >
                                    &gt;
                                </button>
                            </div>
                        </div>
                    </>
                )}
            </div>
        </div>
    )
}

export default RegSuppliers
